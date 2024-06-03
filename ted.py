
import os
import re

from git import *
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import GitLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter


os.environ["OPENAI_API_VERSION"] = "2023-12-01-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
os.environ["AZURE_OPENAI_API_KEY"] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

llm = AzureChatOpenAI(
    deployment_name="gpt-4-32k-0613",
    temperature=0.1,
)

output_parser = StrOutputParser()

loader = GitLoader(
    clone_url="https://github.com/AmadeusITGroup/jetstream-mini-controller.git",
    repo_path="./clone/jetstream-mini-controller/",
    branch="main",
    file_filter=lambda file_path: file_path.endswith(".java"))
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.JAVA,chunk_size=2000, chunk_overlap=200
)
texts = text_splitter.split_documents(data)

vectorstore = FAISS.from_documents(
    texts, embedding=AzureOpenAIEmbeddings()
)
retriever = vectorstore.as_retriever()

template = """You are a skilled java code generator. You read the code provided and you generate answers as the full java source file content that contains the modifications without removing existing parts as comments. Answer the question based on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

chain = ( 
    {
        "context": retriever, "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | output_parser
)

answer = chain.invoke("Produce more unit tests.")

print("-------------------------------------------------\n")
print(answer)
parsed = re.search('```java\n([\w\W]*?)\n```', answer)
diff = ""
if parsed is not None:
    diff = parsed.group(1)
else:
    parsed = re.search('```diff\n([\w\W]*?)\n```', answer)
    diff = parsed.group(1)

f = open("patch.diff", "w")
print("Parsed-------------------------------------------------\n")
print(diff)
f.write(diff)
f.close()

r = Repo('./clone/jetstream-mini-controller/')
r.git.execute(['git', 'apply', '--reject', '--whitespace=fix', '../../patch.diff'])
