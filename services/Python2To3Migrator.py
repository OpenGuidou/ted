import re
import json

from services.Generator import TEDGenerator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import Language

class Python2To3Migrator(TEDGenerator):
    def __init__(self):
        pass

    def runGeneration(self, retriever, llm, output_parser) -> None:
        template = """You are a skilled python developer. Your job is to migrate python 2 projects to python 3.
        You read the code provided and either provide a list of files that needs to be modified during the migration or the full content of the file requested after the migration.
        The generated code should work and should not summarize the changes but provide the full content of the file.
        You return the answer without any explanation in a Json format for the files listing case, and as a text file for the file migration case.

        Here is an example of the expected output for the file listing case:
        {{
            "files": [
                "file1.py",
                "file2.py"
            ]
        }}

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
        parsed = re.search('```json\n([\w\W]*?)\n```', answer)

        if parsed is not None:
            filesAnswer = parsed.group(1)
            files = json.loads(filesAnswer)['files']

            for file in files:
                print("-------------------------------------------------\n")
                print("File to migrate: {}".format(file))
                fileAnswer = chain.invoke("Give me the migrated version of the file {}, with the full content of the file".format(file))
                print(fileAnswer)

                fileParsed = re.search('```migrated\n([\w\W]*?)\n```', fileAnswer)
                if fileParsed is not None:
                    migratedContent = fileParsed.group(1)
                    f = open("clone/" + file, "w")
                    f.write(migratedContent)
                    f.close()
                else:
                    print("File parsing failure")
        else:
            print("Answer parsing failure")
    
    def getFileExtension(self) -> str:
        return ".py"
    
    def getTextFormat(self) -> Language:
        return Language.PYTHON