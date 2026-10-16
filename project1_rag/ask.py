
from project1_rag.rag_chain import build_rag_chain


def main():
    print("=== Ask Your Documents (RAG) ===")

    search_type = input(
        "Choose search type (mmr/similarity) [mmr]: "
    ).strip().lower()

    if not search_type:
        search_type = "mmr"

    if search_type not in ("mmr", "similarity"):
        print("Invalid choice. Please choose mmr or similarity.")
        return

    rag = build_rag_chain(search_type)

    print("\nAsk questions about your documents.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        try:
            result = rag(question)

            print(f"\nAssistant: {result['answer']}")

            sources = sorted({
                doc.metadata.get("source", "Unknown").split("/")[-1]
                for doc in result["docs"]
            })

            print("\nSources:")
            for source in sources:
                print(f"- {source}")

            print()

        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
