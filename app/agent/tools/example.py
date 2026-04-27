from langchain_core.tools import tool


@tool
def echo(text: str) -> str:
    """Return the input text unchanged. Placeholder tool for the template."""
    return text
