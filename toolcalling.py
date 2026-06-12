from dotenv import load_dotenv
load_dotenv()
from langchain_mistralai import ChatMistralAI
from langchain.tools import tool

from rich import print

# 1. crating a tool
@tool
def get_text_length(text : str) -> int:
    """Returns the number of character in a given text"""
    return len(text)

model = ChatMistralAI(model = 'mistral-small-2506')

# 2. tool binding
model_with_tool = model.bind_tools([get_text_length])

result = model_with_tool.invoke("Returns the number of character in a given text : 'hello how are you'")

print(result.tool_calls[0])

print(get_text_length.invoke({'name': 'get_text_length', 'args': {'text': 'hello how are you'}, 'id': 'tDR3nn9Tt', 'type': 'tool_call'}))