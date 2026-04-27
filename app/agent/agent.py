from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from app.agent.prompt import SYSTEM_PROMPT
from app.agent.tools import echo
from app.core.settings import Settings


def build_graph(tools: list[BaseTool] | None = None):
    settings = Settings()
    return create_agent(
        model=settings.agent.MODEL,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )


graph = build_graph([echo])
