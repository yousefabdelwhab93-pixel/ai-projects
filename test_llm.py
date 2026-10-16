
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="mercury-2.5",
    api_key=os.getenv("INCEPTION_API_KEY"),
    base_url=os.getenv("INCEPTION_BASE_URL"),
    temperature=0,
)

response = llm.invoke("Explain RAG in two simple sentences.")
print(response.content)
