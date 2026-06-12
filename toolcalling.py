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

if result.tool_calls :
    tool_call = result.tool_calls[0]
tool_name = tool_call["name"]
tool_args = tool_call["args"]

tool_result = get_text_length.invoke(tool_args)

final_response = model_with_tool.invoke(f"the length of text is {tool_result}")

print(final_response.content)

# print(tool_name)