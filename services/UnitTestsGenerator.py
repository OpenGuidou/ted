import re
from typing import List

from services.Generator import TEDGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import Language

class UnitTestsGenerator(TEDGenerator):

    def runGeneration(self, retriever, llm, output_parser) -> None:

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
        parsed = re.search('\\`\\`\\`java\n([\w\W]*?)\n\\`\\`\\`', answer)
        diff = ""
        if parsed is not None:
            diff = parsed.group(1)
        else:
            parsed = re.search('\\`\\`\\`diff\n([\w\W]*?)\n\\`\\`\\`', answer)
            diff = parsed.group(1)

        f = open("patch.diff", "w")
        print("Parsed-------------------------------------------------\n")
        print(diff)
        f.write(diff)
        f.close()    
    
    
    def getFileExtensions(self) -> List[str]:
        return [".java"]

    def getTextFormat(self) -> Language:
        return Language.JAVA
    