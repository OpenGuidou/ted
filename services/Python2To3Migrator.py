import re
import json
from typing import List

from services.TEDGenerator import TEDGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import Language

class Python2To3Migrator(TEDGenerator):
    def __init__(self):
        pass

    def run_generation(self, retriever, llm, output_parser, clone_dir) -> None:
        template = """You are a skilled python developer. Your job is to migrate python 2 projects to python 3.

        You work in two uses cases: You read the code provided provide a list of files that needs to be modified during the migration, or provide the full content of a file requested after the migration.
        
        For the list of file case: 
        You return the answer without any explanation in a Json format for the files listing case. 
        You should only return the files containing a change to be done for the migration. You should return all the files that need to be modified.
        You should take into account, if applicable, all python files and other files such as Dockerfile, readme, requirements.txt, etc.

        Here is an example of the expected output for the file listing case:
        {{
            "files": [
                "file1.py",
                "Dockerfile", 
                "requirements.txt",
                "Readme.md"
            ]
        }}

        For the file migration case:

        You only take into account the file provided in the question.
        The generated code should work and should not summarize the changes but provide the full content of the file.
        You return the answer as a text file for the file migration case.       

        Here is an example of the expected output for the file migration case:
        ```migrated
        # Migrated file content
        ```
                
        Here are the files that need to be taken into account:
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

        answer = chain.invoke("Give me the list of files that should be modified to migrate from Python 2 to Python 3.")

        print("-------------------------------------------------\n")
        print(answer)
        parsed = re.search('```json\n([\\w\\W]*?)\n```', answer)

        if parsed is not None:
            files_answer = parsed.group(1)
            files = json.loads(files_answer)['files']

            for file in files:
                print("-------------------------------------------------\n")
                print("File to migrate: {}".format(file))
                file_answer = chain.invoke("Give me the migrated version of the file {}, with the full content of the file".format(file))
                print(file_answer)

                file_parsed = re.search('```migrated\n([\\w\\W]*?)\n```', file_answer)
                if file_parsed is not None:
                    migrated_content = file_parsed.group(1)
                    f = open(clone_dir + "/" + file, "w")
                    written = f.write(migrated_content)
                    print("File written: {}, size: {}".format(clone_dir + file, written))
                    f.close()
                else:
                    print("File parsing failure")
        else:
            print("Answer parsing failure")
    
    def get_file_extensions(self) -> List[str]:
        return [".py", ".md", ".txt"]
    
    def get_file_glob(self) -> str:
        return "**/*.py"
    
    def get_text_format(self) -> Language:
        return Language.PYTHON
    
    def get_branch_name(self) -> str:
        return "python2-3"
    
    def get_commit_message(self) -> str:
        return "chore: Python 2 to 3 migration."