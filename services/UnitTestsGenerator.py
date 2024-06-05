import re
from typing import List

from services.TEDGenerator import TEDGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import Language


class UnitTestsGenerator(TEDGenerator):

    def run_generation(self, retriever, llm, output_parser, cloneDir) -> None:
        template = """
        As an advanced Java code generator, your role is to analyze and understand the provided code context.
        You should take into account, if applicable, all java files and other files such as Dockerfile, readme, pom.xml, etc.
        The generated code should compile, be executable and meet the requirements specified in the question.  
        In case the class uses Quarkus framework, a Quarkus test may need.
        
        Context : {context}
        Question : {question}
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

        class_list = chain.invoke("""
        Give me the list of existing java class in the project that you could improve the unit tests for them.
        Return the answer without any explanation in a Json format for the class listing case. 

        Here is an example of the expected output for the file listing case:
        {{
            "files": [
                "AAA.java",
                "BBB.java", 
                "CCC.java"
                ...
            ]
        }}
        """)
        print("-------------------------------------------------\n")
        print(class_list)

        class_name = "ProductService.java"

        explain_question = f"""
        # How to write great unit tests for `{class_name}`
          In this advanced tutorial for experts, we'll use JAVA and Context to write a suite of unit tests to verify the behavior of the class.
          Before writing the unit tests, let's review what each element of the class is doing exactly and what the author's intentions may have been.
        """
        explain_completion = chain.invoke(explain_question)

        print("-------------------------------------------------\n")
        print(explain_completion)
        plan_question = """
        A good unit test suite should aim to:
        - Test the function's behavior for a wide range of possible inputs
        - Test edge cases that the author may not have foreseen
        - Take advantage of the features of Context to make the tests easy to write and maintain
        - Build Objects if needed
        - Be easy to read and understand, with clean code and descriptive names
        - Be deterministic, so that the tests always pass or fail in the same way
        
        the context has many convenient features that make it easy to write and maintain unit tests. We'll use them to write unit tests for class above.
        Don't show the code here.

        We'll want our unit tests to handle the following diverse scenarios (and under each scenario, we include a few examples as sub-bullets):
        """

        prior_text = explain_question + explain_completion + plan_question
        plan_completion = chain.invoke(prior_text)
        print("-------------------------------------------------\n")
        print(plan_completion)

        unit_test = """
        Before going into the individual tests, let's first look at the complete suite of unit tests as a cohesive whole.
        We've added helpful comments to explain what each line does.
        Your task is to generate all the junit tests as a response in one test class based on the scenarios above. 

        - The test should be functional, runnable, compilable and applicable.
        - New tests must be identifiable in their javadoc with @AIGenerated annotation.
        - If there's no existing test class, you should create a new one.
        - If test class exist, keep all the existing tests and methods in the class. Don't change the existing code.
        - Don't test `assertThrows` if there's no exception thrown in the methode.
        - Don't forget to add necessary package and imports for the test class. 
        - Don't import the dependencies not added in the POM.xml.
        - Don't add unnecessary code not included in the project.
        - Don‘t make the methods not exist in the class.
        - Don't show the explains and only return the final complete test class
        
        return the test class in the `java_final` block :
        ```java_final
        the final test class
        ```
        """

        prior_text += plan_completion + unit_test
        unit_test_completion = chain.invoke(prior_text)
        print("-------------------------------------------------\n")
        print(unit_test_completion)
        parsed = re.search('```java_final\n([\\w\\W]*?)\n```', unit_test_completion)
        diff = ""
        if parsed is not None:
            diff = parsed.group(1)

        f = open(f"{class_name}Test.java", "w")
        print("Parsed-------------------------------------------------\n")
        print(diff)
        f.write(diff)
        f.close()

    def get_file_extensions(self) -> List[str]:
        return [".java"]

    def get_text_format(self) -> Language:
        return Language.JAVA

    def get_branch_name(self) -> str:
        return "unit-tests"

    def get_commit_message(self) -> str:
        return "chore: Unit tests generation."
