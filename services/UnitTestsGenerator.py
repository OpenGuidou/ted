import re
from typing import List

from services.Generator import TEDGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import Language

class UnitTestsGenerator(TEDGenerator):

    def runGeneration(self, retriever, llm, output_parser, cloneDir) -> None:

        template = """  You are an advanced java unit test coding assistant. You generate only source code. 
        Your role is to analyze and understand the provided code context. 
        Your task is to generate a functional, runnable, compilable and applicable unit test as a response. 
        The generated code should compile, be executable and meet the requirements specified in the question.  
        In case the class uses Quarkus framework, you should generate both  a Quarkus test and a JUnit test.
        
        Answer the question based on the following context:
        {context}
        
        Question: {question}

        The response should be in the form of a Java class that contains the existing and new tests.
        All the existing tests and methods should be kept in the class, and the new tests should be added at the end of the class.
        New tests must be identifiable in their javadoc with @AIGenerated annotation.
        If there's no existing test class, you should create a new one.
        The response will start with a comment indicating the expected file name of the generated unit test. 
        A suffix is a number that starts from zero. After this code comment, the reponse includes the same package
       declaration and import statements from the class. It also has import statements to the @Test annotation and the assert* methods (e.g.,
assertTrue(...)) from JUnit5. Subsequently, the response contains
the test class’ JavaDoc that specifies the MUT, and how many test
cases to generate. The response ends with the test class declaration
followed by a new line (\n), which will trigger you to generate
code to complete the test class declaration.: 
        ```
            <className><suffix>Test.java >
            <packageDeclaration>
            <importedPackages>
            import org.junit.jupiter.api.Test; 
            import static org.junit.jupiter.api.Assertions.*; 
            
            /** 
            * Test class of {{@link <className>}}. 
            * It contains <numberTests> unit test cases for the 
            * {{@link <className>#<methodSignature>}} method.  
            */ 
            class  <className><suffix>Test {{
            }}
            
        ```
        
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

        answer = chain.invoke("Produce more unit tests for GreetingResource class.")

        print("-------------------------------------------------\n")
        print(answer)
        parsed = re.search('```java\n([\\w\\W]*?)\n```', answer)
        diff = ""
        if parsed is not None:
            diff = parsed.group(1)
        else:
            parsed = re.search('```diff\n([\\w\\W]*?)\n```', answer)
            diff = parsed.group(1)

        f = open("generatedTest.java", "w")
        print("Parsed-------------------------------------------------\n")
        print(diff)
        f.write(diff)
        f.close()    
    
    
    def getFileExtensions(self) -> List[str]:
        return [".java"]

    def getFileGlob(self) -> str:
        return "**/*.java"

    def getTextFormat(self) -> Language:
        return Language.JAVA
    
    def getBranchName(self) -> str:
        return "unit-tests"

    def getCommitMessage(self) -> str:
        return "chore: Unit tests generation."