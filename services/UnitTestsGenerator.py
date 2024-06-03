
from services.Generator import TEDGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

class UnitTestsGenerator(TEDGenerator):

    def runGeneration(self, retriever, llm, output_parser) -> str :

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

        return chain.invoke("Produce more unit tests.")