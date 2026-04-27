MSELECT = "LOCAL"
import json
import os
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

with open("env.json", 'r') as f:
    TOKENCA = json.load(f)[MSELECT]
    MODEL = TOKENCA["model"]
    KEY = TOKENCA["key"]
    BASEURL = TOKENCA["base_url"]

# Create LangChain model
llm = ChatAnthropic(model=MODEL, base_url=BASEURL, api_key=KEY, temperature=0.8)

# Context file paths
CONTEXT_DIR = "./.chat_context"
CONTEXT_FILE = os.path.join(CONTEXT_DIR, "messages.json")
THREAD_FILE = os.path.join(CONTEXT_DIR, "thread_id.txt")

# Ensure context directory exists
os.makedirs(CONTEXT_DIR, exist_ok=True)

# Initialize checkpointer with MemorySaver for state persistence within session
checkpointer = MemorySaver()


def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Sunny, 22°C in {city}"


def load_thread_id() -> str:
    """Load existing thread ID or create new one."""
    if os.path.exists(THREAD_FILE):
        with open(THREAD_FILE, 'r') as f:
            return f.read().strip()
    return None


def save_thread_id(thread_id: str):
    """Save thread ID for next session."""
    with open(THREAD_FILE, 'w') as f:
        f.write(thread_id)


def load_messages() -> list:
    """Load conversation history from file."""
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, 'r') as f:
            return json.load(f)
    return []


def save_messages(messages: list):
    """Save conversation history to file."""
    with open(CONTEXT_FILE, 'w') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def chat():
    # Load existing context
    messages = load_messages()
    thread_id = load_thread_id()

    # Create agent with filesystem backend and checkpointer
    agent = create_deep_agent(
        model=llm,  # Pass LangChain model instance
        tools=[get_weather],
        backend=FilesystemBackend(root_dir="."),
        checkpointer=checkpointer,
        system_prompt="You are a helpful assistant. Answer questions concisely. Use filesystem tools when needed.",
    )

    # Initialize config with thread_id
    config = {"configurable": {"thread_id": thread_id or "default"}}

    if thread_id:
        print(f"Loaded existing conversation (thread: {thread_id})\n")
    else:
        print("Chatbot started. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            # Save context before exiting
            save_messages(messages)
            if not thread_id:
                thread_id = config["configurable"]["thread_id"]
                save_thread_id(thread_id)
            print("Context saved. Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        # Invoke agent with checkpoint
        result = agent.invoke(
            {"messages": messages},
            config=config
        )

        # Update thread_id if new one was created
        if not thread_id:
            thread_id = config["configurable"]["thread_id"]
            save_thread_id(thread_id)

        response = result["messages"][-1].content
        messages.append({"role": "assistant", "content": response})

        print(f"Bot: {response}\n")

        # Auto-save after each exchange
        save_messages(messages)


if __name__ == "__main__":
    chat()
