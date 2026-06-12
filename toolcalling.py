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

result = model.invoke("Returns the number of character in a given text : 'hello how are you'")

result2 = model_with_tool.invoke("Returns the number of character in a given text : 'hello how are you'")
print(result)
print()
print()
print()
print(result2)