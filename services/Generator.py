
from typing import List
from langchain_text_splitters import Language

class TEDGenerator(object):
    
    def runGeneration(self, retriever, llm, output_parser, cloneDir) -> None :
        """Default generator."""
        pass

    def getFileExtensions(self) -> List[str]:
        """Returns the file extension repo code to take into account."""
        pass

    def getFileGlob(self) -> str:
        """Returns the glob to match files in repo code."""
        pass

    def getTextFormat(self) -> Language:
        """Returns the text format of the generator."""
        pass

    def getBranchName(self) -> str:
        """Returns the branch name used to push the branches to."""
        pass

    def getCommitMessage(self) -> str:
        """Returns the commit message used to commit the changes."""
        pass