from dotenv import load_dotenv
load_dotenv()

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Prompt Template
prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in simple words."
)

# 2. Model
model = ChatMistralAI(model = 'mistral-small-2506')

# 3. Output parser
parser = StrOutputParser()

# Step-by-Step manual flow
# Format the prompt
formatted_prompt = prompt.format_messages(topic = 'Machine Learning')

# Call the model
responce = model.invoke(formatted_prompt)

# Parse the Output manually
final_output = parser.parse(responce.content)

print(final_output)