
from typing import List
from langchain_text_splitters import Language

class TEDGenerator(object):
    
    def run_generation(self, retriever, llm, output_parser, clone_dir) -> None :
        """Default generator."""
        pass

    def get_file_extensions(self) -> List[str]:
        """Returns the file extension repo code to take into account."""
        pass

    def get_file_glob(self) -> str:
        """Returns the glob to match files in repo code."""
        pass

    def get_text_format(self) -> Language:
        """Returns the text format of the generator."""
        pass

    def get_branch_name(self) -> str:
        """Returns the branch name used to push the branches to."""
        pass

    def get_commit_message(self) -> str:
        """Returns the commit message used to commit the changes."""
        pass