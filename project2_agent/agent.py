
import os

from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from project2_agent.tools import ALL_TOOLS


load_dotenv(find_dotenv())

SYSTEM_PROMPT = """
You are a helpful teaching assistant.

Rules:
- Use the calculator tool for every mathematical calculation.
- Use get_student_grades for student grade questions.
- Use current_datetime for current date or time questions.
- Use save_note when the user asks to save a note.
- Remember earlier messages in the same conversation.
- Answer briefly and clearly.
"""


def build_agent():
    model = ChatOpenAI(
        model="mercury-2.5",
        api_key=os.getenv("INCEPTION_API_KEY"),
        base_url=os.getenv("INCEPTION_BASE_URL"),
        temperature=0,
    )

    checkpointer = InMemorySaver()

    return create_agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

