import re
from typing import List

from services.TEDGenerator import TEDGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import Language

class UnitTestsGenerator(TEDGenerator):

    def run_generation(self, retriever, llm, output_parser, clone_dir) -> None:

        template = """You are a skilled java code generator. You read the code provided and you generate answers as a applicable git diff. The generated code should work. Answer the question based on the following context:
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
        parsed = re.search('```java\n([\\w\\W]*?)\n```', answer)
        diff = ""
        if parsed is not None:
            diff = parsed.group(1)
        else:
            parsed = re.search('```diff\n([\\w\\W]*?)\n```', answer)
            diff = parsed.group(1)

        f = open("patch.diff", "w")
        print("Parsed-------------------------------------------------\n")
        print(diff)
        f.write(diff)
        f.close()    
    
    
    def get_file_extensions(self) -> List[str]:
        return [".java"]

    def get_file_glob(self) -> str:
        return "**/*.java"

    def get_text_format(self) -> Language:
        return Language.JAVA
    
    def get_branch_name(self) -> str:
        return "unit-tests"

    def get_commit_message(self) -> str:
        return "chore: Unit tests generation."