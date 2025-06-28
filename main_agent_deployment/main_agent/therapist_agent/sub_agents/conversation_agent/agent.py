# from google.adk.agents import LlmAgent
from google.adk.agents import Agent
from google.adk.tools import google_search

conversation_agent = Agent(
    name="conversation_agent",
    model="gemini-2.0-flash",  
    description="An agent that converses with user and offers mental support by empathizing with their feelings and emotions. " \
    "You are a supportive conversation partner who helps users with emotional support. Listen carefully to the user's concerns. " \
    "Show empathy and understanding. Provide gentle guidance and encouragement. " \
    "Keep responses concise but warm. Ask follow-up questions when appropriate."\
    "Instructions:"\
    "- Listen and respond with empathy"\
    "- Keep responses brief and warm (2-3 sentences)"\
    "- Ask follow-up questions when needed"\
    "- Never provide medical advice"\
    "- Direct to professional help if crisis detected",
    tools=[google_search]
)

    # description="An agent that converses with user and offers mental support by empathizing with their feelings and emotions.",

# from google.adk.agents import Agent
# from google.adk.tools import google_search

# root_agent = Agent(
#     name="Conversation Agent",
#     model = "gemini-2.0-flash",
#     description="An agent that converses with user and offers mental support by empathizing with their feelings and emotions.",
#     instructions="You're a helpful assistant. Keep replies short and friendly.",
#     tools = [google_search]
# )
