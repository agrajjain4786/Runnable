from dotenv import load_dotenv
load_dotenv()

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

model = ChatMistralAI(model = 'mistral-small-2506')
parser = StrOutputParser()

code_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a code generator"),
    ("human", "{topic}")
])

explain_prompt = ChatPromptTemplate.from_messages([
    ("system","you are a helpful assistant who explain code in simple terms."),
    ("human","explain the following code in simple words:\n{code}")
])

seq = code_prompt | model | parser 

seq2 = RunnableParallel(
    {"code" : RunnablePassthrough(),
     "explanation" : explain_prompt | model | parser
    }
)

chain = seq | seq2
result = chain.invoke({"topic" : "write a code on palindrome in python"})

print(result['code'])
print(result['explanation'])