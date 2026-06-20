"""
Core agent setup: tools, LLM, and a per-session agent factory.

The original CLI version asked for tool approval via input(). That doesn't
work over a websocket, so the approval check has been swapped out for
`session.request_approval(...)`, which blocks the worker thread until the
browser sends back an approve/deny decision (see main.py / Session).
"""

import os
import requests
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from tavily import TavilyClient

load_dotenv()

# ============================================================
# WEATHER TOOL
# ============================================================
@tool
def get_weather(city: str) -> str:
    """Get current weather information for a given city."""
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={weather_api_key}&units=metric"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    if str(data.get("cod")) != "200":
        return f"Error: {data.get('message', 'Could not fetch weather')}"

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    return f"Weather in {city}: {desc}, {temp}°C"


# ============================================================
# NEWS TOOL
# ============================================================
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def get_news(city: str) -> str:
    """Get the latest news related to a given city."""
    response = tavily_client.search(
        query=f"latest news of {city}",
        search_depth="basic",
        max_results=3,
    )

    results = response.get("results", [])
    if not results:
        return f"No news found for {city}"

    news_list = []
    for r in results:
        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")
        news_list.append(f" - {title}\n  🔗 {url}\n  📝 {snippet[:100]}...")

    return f"Latest news in {city}:\n\n" + "\n\n".join(news_list)


# ============================================================
# LLM
# ============================================================
llm = ChatMistralAI(model="mistral-small-2506")


# ============================================================
# PER-SESSION AGENT FACTORY
# ============================================================
def build_agent(session):
    """
    Build a fresh agent bound to one websocket session, so each browser
    tab gets its own isolated human-approval gate.
    """

    @wrap_tool_call
    def human_approval(request, handler):
        tool_name = request.tool_call["name"]
        tool_args = request.tool_call.get("args", {})

        approved = session.request_approval(tool_name, tool_args)

        if not approved:
            return ToolMessage(
                content="Tool call denied by user.",
                tool_call_id=request.tool_call["id"],
            )
        return handler(request)

    return create_agent(
        llm,
        tools=[get_weather, get_news],
        system_prompt="You are a helpful City Assistant.",
        middleware=[human_approval],
    )
