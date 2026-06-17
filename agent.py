from dotenv import load_dotenv
load_dotenv()

import os
import requests

from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from tavily import TavilyClient
from rich import print

# Weather Tool
@tool
def get_weather(city : str) -> str :
    """Get Current weather of a city"""
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")  
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    responce = requests.get(url)
    data = responce.json()

    if str(data.get("cod")) != "200" :
        return f"Error : {data.get("message", "Could not fetch weather")}"

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    return f"Weather in {city} : {desc}, {temp}°C"

# Tavily news tool

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def get_news(city: str)-> str:
    """Get the latest news of the city"""
    responce = tavily_client.search(
        query=f"latest news of {city}",
        search_depth="basic",
        max_results=3,
    )

    results = responce.get("results", [])
    if not results:
        return f"No news found for {city}"

    news_list = []

    for r in results :
        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")

        news_list.append(
            f" - {title}\n  🔗 {url}\n 📝 {snippet[:100]}..."
        )

    return f"Latest news in {city}: \n\n"+ "\n\n".join(news_list)

print(get_news.invoke("AGRA"))