# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# IMPORT REQUIRED LIBRARIES
# ============================================================
import os
import requests

from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from tavily import TavilyClient
from rich import print
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call



# ============================================================
# WEATHER TOOL
# ============================================================
@tool
def get_weather(city: str) -> str:
    """
    Get current weather information for a given city.
    """

    # Fetch API key from environment variables
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")

    # OpenWeather API endpoint
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={weather_api_key}&units=metric"
    )

    # Make API request
    responce = requests.get(url)
    data = responce.json()

    # Handle invalid city or API errors
    if str(data.get("cod")) != "200":
        return f"Error : {data.get('message', 'Could not fetch weather')}"

    # Extract weather details
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]

    return f"Weather in {city} : {desc}, {temp}°C"


# ============================================================
# TAVILY SEARCH CLIENT
# ============================================================
tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# ============================================================
# NEWS TOOL
# ============================================================
@tool
def get_news(city: str) -> str:
    """
    Get the latest news related to a given city.
    """

    # Search latest news using Tavily
    responce = tavily_client.search(
        query=f"latest news of {city}",
        search_depth="basic",
        max_results=3,
    )

    results = responce.get("results", [])

    # Handle no results found
    if not results:
        return f"No news found for {city}"

    news_list = []

    # Format search results
    for r in results:
        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")

        news_list.append(
            f" - {title}\n"
            f"  🔗 {url}\n"
            f"  📝 {snippet[:100]}..."
        )

    return (
        f"Latest news in {city}:\n\n"
        + "\n\n".join(news_list)
    )

# ============================================================
# INITIALIZE MISTRAL LLM
# ============================================================
llm = ChatMistralAI(
    model="mistral-small-2506"
)


@wrap_tool_call
def human_approval(request,handler):
    """Ask for human approval before every tool call."""
    tool_name = request.tool_call["name"]
    confirm = input(f"Agent wants to call '{tool_name}'. Approve? (Y/N) → ")

    if confirm.lower() != "y":
        return ToolMessage(
            content = "Tool call denied by user.",
            tool_call_id = request.tool_call["id"]
        )
    return handler(request)

# ============================================================
# INITIALIZE AGENT BY CREATE_AGENT
# ============================================================
agent = create_agent(
    llm,
    tools = [get_weather,get_news],
    system_prompt="You are a helpful City Assistent.",
    middleware=[human_approval],
)

print("City Agent   |   Type exit to quit")

while True:
    print("-"*50)
    user_input = input("You → ")

    if user_input.lower() == "exit":
        break
    result = agent.invoke({
        "messages" : [{"role" : "user", "content" : user_input}]   
    })
    print("Bot → ",result['messages'][-1].content)

    print("-"*50)