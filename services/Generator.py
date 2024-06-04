
from typing import List
from langchain_text_splitters import Language

class TEDGenerator(object):
    
    def runGeneration(self, retriever, llm, output_parser) -> None :
        """Default generator."""
        pass

    def getFileExtensions(self) -> List[str]:
        """Returns the file extension repo code to take into account."""
        pass

    def getTextFormat(self) -> Language:
        """Returns the text format of the generator."""
        pass