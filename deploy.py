import os
import sys
from vertexai import agent_engines, init
from vertexai.preview import reasoning_engines
from root_agent import create_root_agent
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")


# Function to read existing resource name from file
def get_existing_resource_name():
    """Read existing resource name from deployed_agent_info.txt if it exists"""
    file_path = "deployed_agent_info.txt"

    if not os.path.exists(file_path):
        print("📄 No existing deployment file found - will create new deployment")
        return None

    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.startswith("Resource Name:"):
                    resource_name = line.split(":", 1)[1].strip()
                    print(f"📋 Found existing resource: {resource_name}")
                    return resource_name

        print(
            "⚠️  Deployment file exists but no resource name found - will create new deployment"
        )
        return None

    except Exception as e:
        print(f"❌ Error reading deployment file: {e}")
        print("🔄 Will create new deployment")
        return None


# Automatically detect existing resource
EXISTING_RESOURCE_NAME = get_existing_resource_name()

# Validate environment variables
if not PROJECT_ID:
    raise ValueError("❌ PROJECT_ID environment variable is required")
if not LOCATION:
    raise ValueError("❌ LOCATION environment variable is required")

print(f"🔧 Project: {PROJECT_ID}")
print(f"🌍 Location: {LOCATION}")

STAGING_BUCKET = f"gs://{PROJECT_ID}-agent-staging-bucket"
print(f"🪣 Staging Bucket: {STAGING_BUCKET}")

# CHANGE THIS LINE: Initialize Vertex AI with staging bucket
init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Create updated app
app = reasoning_engines.AdkApp(
    agent=create_root_agent(),  # Your updated agent
    enable_tracing=True,
)

requirements = [
    "google-cloud-aiplatform[agent_engines,adk]>=1.60.0",
    "google-genai>=0.8.0",
    "aiohttp>=3.8.0",
    "firebase-admin>=6.5.0",
    "numpy>=1.24.0",
    "pandas>=1.5.0",
    "pydantic",
    "cloudpickle",
]

# Automatically decide between update or create
if EXISTING_RESOURCE_NAME:
    print("🔄 Updating existing agent deployment...")
    try:
        remote_agent = agent_engines.update(
            resource_name=EXISTING_RESOURCE_NAME,
            app=app,
            requirements=requirements,
            extra_packages=["."],
        )
        print("✅ Agent updated successfully!")
        operation_type = "Updated"
    except Exception as e:
        print(f"❌ Update failed: {e}")
        print("🔄 Falling back to creating new deployment...")
        remote_agent = agent_engines.create(
            app,
            requirements=requirements,
            extra_packages=["."],
        )
        print("✅ New agent deployed successfully!")
        operation_type = "Created (fallback)"
else:
    print("🚀 Creating new agent deployment...")
    remote_agent = agent_engines.create(
        app,
        requirements=requirements,
    )
    print("✅ New agent deployed successfully!")
    operation_type = "Created"

print(f"📍 Resource ID: {remote_agent.resource_name}")

def get_deployment_count():
    """Get the current deployment count from the file"""
    try:
        with open("deployed_agent_info.txt", "r") as f:
            for line in f:
                if line.startswith("Deployment Count:"):
                    return int(line.split(":", 1)[1].strip())
    except:
        pass
    return 0

with open("deployed_agent_info.txt", "w") as f:
    f.write(f"Resource Name: {remote_agent.resource_name}\n")
    f.write(f"Project: {PROJECT_ID}\n")
    f.write(f"Location: {LOCATION}\n")
    f.write(f"Operation: {operation_type}\n")
    f.write(f"Last Updated: {datetime.now().isoformat()}\n")
    f.write(f"Deployment Count: {get_deployment_count() + 1}\n")

print("💾 Deployment info saved to 'deployed_agent_info.txt'")
