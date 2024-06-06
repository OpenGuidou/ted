from datetime import datetime
import time
import os
import json
import re
from typing import List
import fnmatch

from services.TEDGenerator import TEDGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import Language


class UnitTestsGenerator(TEDGenerator):

    def run_generation(self, retriever, llm, output_parser, clone_dir) -> None:

        template = """You are an advanced java unit test coding assistant. 
        Your role is to analyze and understand the provided code context. 
   
        You only generate source code.
        Your task is to generate a functional, runnable, compilable and applicable unit tests class as a response.
        You only take into account the file provided in the question. 
        The generated code must compile, be executable and meet the requirements specified in the question. Moreover, it must
        contain the full content of the file.
        In case the tested class uses Quarkus framework, you should generate both Quarkus tests and Junit tests.

        When the generation takes more than 300 seconds, you stop the process and return the current state of the generated code
        with @abortedGEneration annotation in the class javadoc.

        Here is an example of the expected output for the unit test generation:
        The response should be in the form of a Java class that contains the existing and new tests.
        All the existing tests and methods should be kept in the class, and the new tests should be added at the end of the class.
        New test methods must be identifiable with a javadoc comment containing @TedAIGenerated <timestamp> annotation and a description of the purpose of the test, like : 
        /**
         * Test getting a product by ID that does not exist in the ProductService.
         * @TedAIGenerated 20240606113022
         */
        If there isn't any existing test class, you should create a new one.
        The response will start with the same package declaration and import statements than the tested class. 
        It also has import statements to the @Test annotation and the assert* methods (e.g.,assertTrue(...)) from JUnit5. 
        Subsequently, the response contains the test class’ JavaDoc that specifies the MUT, and the number of test cases. 
        The response ends with the test class declaration followed by a new line (\n), which will trigger you to generate code to
        complete the test class declaration.
        - Don't test `assertThrows` if there's no exception thrown in the method.
        - Don't forget to add necessary package and imports for the test class. 
        - Don't import the dependencies not added in the POM.xml.
        - Don't add unnecessary code not included in the project.
        - Don‘t use non existing class constructors (very important point): 
        
        ```java
        <packageDeclaration>
        <importedPackages>
        import org.junit.jupiter.api.Test; 
        import static org.junit.jupiter.api.Assertions.*;   
        /** 
         * Test class of {{@link <className>}}. 
         * It contains <numberTests> unit test cases.  
        */ 
        class  <className>Test {{ 

        ```



        Answer the question based on the following context:
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
  
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        global_timer_start = time.time()
        for java_file in self.list_java_files( clone_dir + 'src/main'):
            print("-------------------------------------------------\n")
            local_timer_start = time.time()
            print("Class to add unit tests to: {}".format(java_file))
            file_answer = chain.invoke("Produce more unit tests for {} class with timestamp {}. All methods should be covered".format(java_file, timestamp ))
            print(file_answer)
            file_parsed = re.search('```java\n([\\w\\W]*?)\n```', file_answer)
            if file_parsed is not None:
                enhanced_unit_class = file_parsed.group(1)
                test_class_path = java_file.replace(clone_dir + '/src/main', clone_dir + 'src/test', 1)
                test_class_path = self.add_test_after_class_name_extension(test_class_path)
                print ("Junit created/updated: {}".format(test_class_path))
                # junit are in the same package than the source  but in test root.
                print ("Working directory:")
                print(os.getcwd())
                # in case an intermediate directory does not exist, create it.
                dir_name = os.path.dirname(test_class_path)
                os.makedirs(dir_name, exist_ok=True)
                with open("./{}".format(test_class_path), 'w') as f:
                    written = f.write(enhanced_unit_class)
                print("File written: {}, size: {}".format("./{}".format(test_class_path), written))
                f.close()
            else:
                print("No need to add unit test for the file.")
            local_timer_end = time.time()
            local_elapsed_time = local_timer_end - local_timer_start
            print ("Time elapsed for the last java file repo process: {}".format(local_elapsed_time))
        global_timer_end = time.time()
        global_elapsed_time = global_timer_end - global_timer_start
        print("-------------------------------------------------\n")
        print("-------------------------------------------------\n")
        print ("Time elapsed for the full repo process: {}".format(global_elapsed_time))
 
    
    def get_file_extensions(self) -> List[str]:
        return [".java"]

    def get_text_format(self) -> Language:
        return Language.JAVA

    def get_branch_name(self) -> str:
        return "unit-tests"

    def get_commit_message(self) -> str:
        return "chore: Unit tests generation."
    
    def list_java_files(self, directory):
        java_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if fnmatch.fnmatch(file, '*.java'):
                    java_files.append(os.path.join(root, file))
        return java_files
    
    def add_test_after_class_name_extension(self, file_path):
        base_name = os.path.basename(file_path)
        new_base_name = re.sub(r'(.*)\.java', r'\1Test.java', base_name)
        return os.path.join(os.path.dirname(file_path), new_base_name)
