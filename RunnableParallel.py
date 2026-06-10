from dotenv import load_dotenv
load_dotenv()

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda
# components
# :- Model
model = ChatMistralAI(model = 'mistral-small-2506')
# :- Output parser
parser = StrOutputParser()

# two different prompts
# Short Prompt Template
short_prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in 1-2 lines."
)
# Detailed Prompt Template
detail_prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in detail."
)

# input
topic = 'machine learning'
# by using runnalbes

chain = RunnableParallel({
    "short" :RunnableLambda(lambda x : x ['short']) |short_prompt | model | parser ,
    "detailed" :RunnableLambda(lambda x : x ['detailed']) | detail_prompt | model | parser
})
result = chain.invoke({
    "short" : {'topic' : topic},
    "detailed" :{'topic' : "oops in java and python"}
})
print(result['short'])
print(result['detailed'])