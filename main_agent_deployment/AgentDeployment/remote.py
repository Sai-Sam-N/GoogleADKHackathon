import os
import sys

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

# Ensure this import path is correct for your root_agent
from main_agent.therapist_agent.agent import root_agent

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_string("user_id", "test_user", "User ID for session operations.")
flags.DEFINE_string("session_id", None, "Session ID for operations.")
flags.DEFINE_bool("create", False, "Creates a new deployment.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployment.")
flags.DEFINE_bool("list", False, "Lists all deployments.")
flags.DEFINE_bool("create_session", False, "Creates a new session.")
flags.DEFINE_bool("list_sessions", False, "Lists all sessions for a user.")
flags.DEFINE_bool("get_session", False, "Gets a specific session.")
flags.DEFINE_bool("send", False, "Sends a message to the deployed agent.")
flags.DEFINE_string(
    "message",
    "Shorten this message: Hello, how are you doing today?",
    "Message to send to the agent.",
)
flags.mark_bool_flags_as_mutual_exclusive(
    [
        "create",
        "delete",
        "list",
        "create_session",
        "list_sessions",
        "get_session",
        "send",
    ]
)

# --- Helper function to get full resource name ---
def _get_full_agent_resource_name(resource_id: str) -> str:
    """Constructs the full agent resource name."""
    # Ensure FLAGS.project_id and FLAGS.location are set before calling this
    return f"projects/{FLAGS.project_id}/locations/{FLAGS.location}/agentEngines/{resource_id}"


# --- DEPLOYMENT FUNCTIONS ---

def create() -> None:
    """Creates a new deployment."""
    app_wrapper = reasoning_engines.AdkApp( # Renamed 'app' to 'app_wrapper' to avoid conflict with absl.app
        agent=root_agent,
        enable_tracing=True,
    )

    # Now deploy to Agent Engine
    remote_app = agent_engines.create(
        agent_engine=app_wrapper, # Use the renamed variable here
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
            # Include other necessary requirements, e.g., if your agent uses pydantic
            "cloudpickle==3.1.1", # Often required for ADK deployments
            "pydantic==2.11.7",   # If your agent uses Pydantic
        ],
        extra_packages=["./main_agent/therapist_agent"],
    )
    print(f"Created remote app: {remote_app.resource_name}")


def delete(resource_id: str) -> None:
    """Deletes an existing deployment."""
    full_resource_name = _get_full_agent_resource_name(resource_id)
    remote_app = agent_engines.AgentEngine.load(full_resource_name) # Using load()
    remote_app.delete(force=True)
    print(f"Deleted remote app: {full_resource_name}")


# def list_deployments() -> None:
#     """Lists all deployments."""
#     deployments = agent_engines.list()
#     if not deployments:
#         print("No deployments found.")
#         return
#     print("Deployments:")
#     for deployment in deployments:
#         # --- CORRECTED: Accessing state attribute and more details ---
#         print(f"- Resource Name: {deployment.resource_name}, State: {deployment.state.name}")
#         print(f"  Display Name: {deployment.display_name}")
#         print(f"  Create Time: {deployment.create_time}")
#         print(f"  Last Update Time: {deployment.update_time}")

def _get_full_agent_resource_name(resource_id: str) -> str:
    """Constructs the full agent resource name."""
    # Ensure FLAGS.project_id and FLAGS.location are set before calling this
    return f"projects/{FLAGS.project_id}/locations/{FLAGS.location}/agentEngines/{resource_id}"


# --- DEPLOYMENT FUNCTIONS ---

def create() -> None:
    """Creates a new deployment."""
    app_wrapper = reasoning_engines.AdkApp( # Renamed 'app' to 'app_wrapper' to avoid conflict with absl.app
        agent=root_agent,
        enable_tracing=True,
    )

    remote_app = agent_engines.create(
        agent_engine=app_wrapper,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
            "cloudpickle==3.1.1", # Often required for ADK deployments
            "pydantic==2.11.7",   # If your agent uses Pydantic
        ],
        extra_packages=["./main_agent"],
    )
    print(f"Created remote app: {remote_app.resource_name}")


def delete(resource_id: str) -> None:
    """Deletes an existing deployment."""
    full_resource_name = _get_full_agent_resource_name(resource_id)
    remote_app = agent_engines.AgentEngine.load(full_resource_name)
    remote_app.delete(force=True)
    print(f"Deleted remote app: {full_resource_name}")


def list_deployments() -> None:
    """Lists all deployments."""
    deployments = agent_engines.list()
    if not deployments:
        print("No deployments found.")
        return
    print("Deployments:")
    for deployment in deployments:
        # --- CORRECTED LINE FOR list_deployments ---
        # The 'state' attribute on AgentEngine objects from agent_engines.list()
        # is a string representing the state (e.g., "ACTIVE", "CREATING").
        # It does not have a .name attribute.
        # print(type(deployment))
        # deployment_state = deployment.state if hasattr(deployment, 'state') else "UNKNOWN_STATE"
        
        # print(f"- Resource Name: {deployment.resource_name}, State: {deployment_state}")
        print(f"- Resource Name: {deployment.resource_name}")
        print(f"  Display Name: {deployment.display_name}")
        print(f"  Create Time: {deployment.create_time}")
        print(f"  Last Update Time: {deployment.update_time}")


# --- SESSION MANAGEMENT FUNCTIONS ---

def create_session(resource_id: str, user_id: str) -> None:
    """Creates a new session for the specified user."""
    full_resource_name = _get_full_agent_resource_name(resource_id)
    remote_app = agent_engines.AgentEngine.load(full_resource_name) # Using load()
    
    remote_session = remote_app.create_session(user_id=user_id)
    print("Created session:")
    # --- CORRECTED: Using dot notation for attributes ---
    print(f"  Session Full Resource Name: {remote_session.name}")
    # Extract the short ID from the full resource name
    session_short_id = remote_session.name.split('/')[-1]
    print(f"  Session ID (short): {session_short_id}")
    print(f"  User ID: {remote_session.user_id}")
    print(f"  App name: {remote_session.app_name}") # May be None if not set
    print(f"  Last update time: {remote_session.last_update_time}")
    print(f"  Create time: {remote_session.create_time}")
    print("\nUse this Session ID (short) with --session_id when sending messages.")


def list_sessions(resource_id: str, user_id: str) -> None:
    """Lists all sessions for the specified user."""
    full_resource_name = _get_full_agent_resource_name(resource_id)
    remote_app = agent_engines.AgentEngine.load(full_resource_name) # Using load()
    sessions = remote_app.list_sessions(user_id=user_id)
    print(f"Sessions for user '{user_id}':")
    if not sessions:
        print("  No sessions found for this user.")
        return
    for session in sessions:
        # --- CORRECTED: Using dot notation for attributes ---
        session_short_id = session.name.split('/')[-1]
        print(f"- Session ID: {session_short_id}, Last update: {session.last_update_time}")


def get_session(resource_id: str, user_id: str, session_id: str) -> None:
    """Gets a specific session."""
    full_resource_name = _get_full_agent_resource_name(resource_id)
    remote_app = agent_engines.AgentEngine.load(full_resource_name) # Using load()
    session = remote_app.get_session(user_id=user_id, session_id=session_id)
    print("Session details:")
    # --- CORRECTED: Using dot notation for attributes ---
    print(f"  Full Resource Name: {session.name}")
    print(f"  Session ID (short): {session.name.split('/')[-1]}")
    print(f"  User ID: {session.user_id}")
    print(f"  App name: {session.app_name}") # May be None
    print(f"  Last update time: {session.last_update_time}")
    print(f"  Create time: {session.create_time}")


def send_message(resource_id: str, user_id: str, session_id: str, message: str) -> None:
    """Sends a message to the deployed agent."""
    # The project_id, location, and bucket are globally initialized in main
    # Ensure they are set via flags or env vars before calling this function
    if not FLAGS.project_id or not FLAGS.location:
        print("Project ID and Location are required. Please set --project_id and --location flags or GOOGLE_CLOUD_PROJECT/GOOGLE_CLOUD_LOCATION env vars.")
        return

    full_resource_name = _get_full_agent_resource_name(resource_id)
    remote_app = agent_engines.AgentEngine.load(full_resource_name) # Using load()

    print(f"Sending message to resource id {resource_id}:")
    print(f"Sending message to session {session_id}:")
    print(f"User ID: {user_id}")
    print(f"Message: {message}")
    print("\nAgent Response:")
    
    try:
        for event in remote_app.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            # --- CORRECTED: Parsing QueryEvent to get actual text/data ---
            # print(f"DEBUG: Raw Event Received: {event}") # Uncomment for full event object
            if event.output:
                if event.output.parts:
                    for part in event.output.parts:
                        if part.text:
                            print(f"AGENT TEXT: {part.text}")
                        elif part.function_call:
                            print(f"AGENT FUNCTION CALL: {part.function_call.function_name} args={part.function_call.args}")
                        # Add more conditions for other part types (e.g., tool_code_output, data)
                elif event.output.text: # Fallback for simpler text outputs
                    print(f"AGENT TEXT: {event.output.text}")
            elif event.actions: # If the agent is performing actions (e.g., tool usage)
                for action in event.actions:
                    print(f"AGENT ACTION: Tool={action.tool_code}, Parameters={action.parameters}")
            elif event.end_turn:
                print("--- Agent Turn Ended ---")
            else:
                # Catch any other unexpected event types
                print(f"UNKNOWN AGENT EVENT TYPE: {event}")

    except Exception as e:
        print(f"\nERROR: An error occurred during the streaming query on the client side: {e}")
        print("This often means the deployed agent crashed or encountered an unhandled error.")
        print("--- CHECK GOOGLE CLOUD LOGGING FOR THE DEPLOYED AGENT (ReasoningEngine) ---")


def main(argv=None):
    """Main function that can be called directly or through app.run()."""
    # Parse flags first
    if argv is None:
        argv = flags.FLAGS(sys.argv)
    else:
        argv = flags.FLAGS(argv)

    load_dotenv()

    # Now we can safely access the flags or environment variables
    # Ensure project_id, location, and bucket are passed via CLI flags or set in .env
    project_id = FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")
    user_id = FLAGS.user_id

    if not project_id:
        print("Error: Missing required GCP project ID. Set with --project_id flag or GOOGLE_CLOUD_PROJECT env var.")
        return
    elif not location:
        print("Error: Missing required GCP location. Set with --location flag or GOOGLE_CLOUD_LOCATION env var.")
        return
    elif not bucket:
        print("Error: Missing required GCP bucket. Set with --bucket flag or GOOGLE_CLOUD_STAGING_BUCKET env var.")
        return

    # Initialize Vertex AI globally for all subsequent SDK calls
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )

    # Dispatch based on flags
    if FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("Error: --resource_id is required for delete.")
            return
        delete(FLAGS.resource_id)
    elif FLAGS.list:
        list_deployments()
    elif FLAGS.create_session:
        if not FLAGS.resource_id:
            print("Error: --resource_id is required for create_session.")
            return
        create_session(FLAGS.resource_id, user_id)
    elif FLAGS.list_sessions:
        if not FLAGS.resource_id:
            print("Error: --resource_id is required for list_sessions.")
            return
        list_sessions(FLAGS.resource_id, user_id)
    elif FLAGS.get_session:
        if not FLAGS.resource_id:
            print("Error: --resource_id is required for get_session.")
            return
        if not FLAGS.session_id:
            print("Error: --session_id is required for get_session.")
            return
        get_session(FLAGS.resource_id, user_id, FLAGS.session_id)
    elif FLAGS.send:
        if not FLAGS.resource_id:
            print("Error: --resource_id is required for send.")
            return
        if not FLAGS.session_id:
            print("Error: --session_id is required for send.")
            return
        send_message(FLAGS.resource_id, user_id, FLAGS.session_id, FLAGS.message)
    else:
        print(
            "Please specify one of: --create, --delete, --list, --create_session, --list_sessions, --get_session, or --send"
        )


if __name__ == "__main__":
    app.run(main)