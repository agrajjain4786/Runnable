from dotenv import load_dotenv
load_dotenv()
from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage

from rich import print

# 1. crating a tool
@tool
def get_text_length(text : str) -> int:
    """Returns the number of character in a given text"""
    return len(text)

tools = {
    "get_text_length" : get_text_length
}
model = ChatMistralAI(model = 'mistral-small-2506')

# 2. tool binding
model_with_tool = model.bind_tools([get_text_length])
prompt = input("You : ")
messages = []
query = HumanMessage(prompt)
messages.append(query)

result = model_with_tool.invoke(messages)

messages.append(result)

if result.tool_calls:
    tool_name = result.tool_calls[0]["name"]
    tool_messge = tools[tool_name].invoke(result.tool_calls[0])
    messages.append(tool_messge)

# print(messages)
result = model_with_tool.invoke(messages)
print("BOT : ",result.content)