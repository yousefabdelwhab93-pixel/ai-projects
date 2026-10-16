# AI Projects Hub

An interactive Streamlit application that combines two AI projects: a Retrieval-Augmented Generation (RAG) chatbot for document question answering and a tool-calling AI teaching assistant with conversation memory.

## Projects

### 1. Ask Your Documents — RAG
- Load PDF and TXT documents.
- Split documents into chunks and generate embeddings locally using Sentence Transformers.
- Store and retrieve document embeddings with ChromaDB.
- Support MMR and similarity-based retrieval.
- Generate answers grounded in the provided documents.
- Display source files and PDF page references.
- Return a fallback response when the answer is not supported by the indexed documents.

### 2. Teaching Assistant Agent
- Perform mathematical calculations using a safe AST-based calculator.
- Retrieve student grades from a sample dataset.
- Get the current local date and time.
- Save notes to a text file.
- Use LangGraph memory to maintain conversation context within a thread.
- Inspect tool calls and their results.

### Streamlit Interface
- Switch between the RAG chatbot and the Teaching Assistant Agent.
- Chat through a single web interface.
- View document sources and optional tool activity.
- Start a new agent conversation.

## Technologies

- Python
- Streamlit
- LangChain
- LangGraph
- ChromaDB
- Sentence Transformers
- Hugging Face
- Inception Labs API
- PyPDF

## Project Structure

```text
ai-projects/
├── app.py
├── .env.example
├── .gitignore
├── requirements.txt
├── project1_rag/
│   ├── data/
│   ├── config.py
│   ├── ingest.py
│   ├── rag_chain.py
│   └── ask.py
└── project2_agent/
    ├── tools.py
    ├── agent.py
    ├── main.py
    └── notes.txt
```

The `chroma_db/` directory is generated locally by the ingestion process and should not be committed to Git.

## Prerequisites

- Python 3.10 or a compatible version supported by the installed dependencies.
- An Inception Labs API key.
- Git and GitHub for version control.

## Installation

1. Clone the repository and open its root directory in VS Code.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows, activate it with:

   ```powershell
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your own API key.

5. Place your PDF and TXT documents inside `project1_rag/data/`.

## Build the RAG Database

From the repository root, run:

```bash
python -m project1_rag.ingest
```

This loads the documents, splits them into chunks, generates embeddings, and creates the local Chroma database.

## Run the Application

Start the Streamlit interface:

```bash
python -m streamlit run app.py
```

Alternatively, run the command-line applications from the repository root:

```bash
python -m project1_rag.ask
python -m project2_agent.main
```

## Environment Variables

The application uses these environment variables:

- `INCEPTION_API_KEY`: Your Inception Labs API key.
- `INCEPTION_BASE_URL`: The API base URL used by the application.

Never commit your real `.env` file or expose API keys in source code.

## Testing

The project was manually tested for:

- RAG answers, source references, and out-of-scope questions.
- MMR and similarity retrieval.
- Calculator operations and student grade lookup.
- Date/time retrieval and note saving.
- Agent conversation memory and thread isolation.
- Tool-call visibility in the Streamlit interface.

## Limitations

- Agent memory uses an in-memory checkpointer and is not persistent across application restarts.
- Student grades are sample data defined in the project.
- RAG answers depend on the quality and content of the indexed documents.
- API access and usage may be subject to provider limits.

## Security

- API keys must be stored in `.env`.
- `.env`, `.venv/`, generated databases, and Python cache files should be excluded from version control.

## License

No license has been specified yet.
