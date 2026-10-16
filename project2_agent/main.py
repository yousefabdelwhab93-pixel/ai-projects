
from project2_agent.agent import build_agent


def main():
    agent = build_agent()

    thread_id = input(
        "Enter thread ID [default]: "
    ).strip() or "default"

    verbose = input(
        "Show tool calls? (y/n): "
    ).strip().lower() == "y"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print("\nTeaching Assistant Agent")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        try:
            for update in agent.stream(
                {
                    "messages": [
                        {"role": "user", "content": user_input}
                    ]
                },
                config=config,
                stream_mode="updates",
            ):
                for node_name, node_data in update.items():
                    messages = node_data.get("messages", [])

                    for message in messages:
                        if message.type == "ai":
                            if verbose and message.tool_calls:
                                for tool_call in message.tool_calls:
                                    print(
                                        f"\n[Tool call] "
                                        f"{tool_call['name']}: "
                                        f"{tool_call['args']}"
                                    )

                            elif message.content:
                                print(
                                    f"\nAssistant: {message.content}"
                                )

                        elif message.type == "tool" and verbose:
                            print(
                                f"[Tool result] "
                                f"{message.name}: {message.content}"
                            )

        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()
