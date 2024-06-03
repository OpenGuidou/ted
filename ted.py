
import os
import re
import argparse

from services.UnitTestsGenerator import UnitTestsGenerator
from services.Python2To3Migrator import Python2To3Migrator
from git import *
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.document_loaders import GitLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter


def main():

    """
    Main function of this script. Promotes chart changes from one repository branch to another, given a source commit.
    """
    # Parses input arguments, initializes various local variables and perform basic checks on input parameters
    arguments = parse_arguments()

    git_url = arguments.git_repo
    branch = arguments.branch
    ted_flavor = arguments.ted_flavor

    if (branch is None):
        branch = "main"

    generator = None
    match ted_flavor:
        case "unit-tests":
            print("Unit tests generation.")
            generator = UnitTestsGenerator()
        case "python2-3":
            print(f"Python 2 to 3 migration.")
            generator = Python2To3Migrator()
        case _:
            print("Unsupported ted flavor.")
            return

    os.environ["OPENAI_API_VERSION"] = "2023-12-01-preview"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
    os.environ["AZURE_OPENAI_API_KEY"] = "XXXXXXXXXXXXXXXXXXXXXXXXXX"

    llm = AzureChatOpenAI(
        deployment_name="gpt-4-32k-0613",
        temperature=0.5,
    )

    output_parser = StrOutputParser()

    loader = GitLoader(
        clone_url=git_url,
        repo_path="./clone/",
        branch=branch,
        file_filter=lambda file_path: file_path.endswith(".java"))
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JAVA,chunk_size=2000, chunk_overlap=200
    )
    texts = text_splitter.split_documents(data)

    vectorstore = FAISS.from_documents(
        texts, embedding=AzureOpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()
    
    answer = generator.runGeneration(retriever, llm, output_parser)    

    print("-------------------------------------------------\n")
    print(answer)
    parsed = re.search('```java\n([\w\W]*?)\n```', answer)
    diff = ""
    if parsed is not None:
        diff = parsed.group(1)
    else:
        parsed = re.search('```diff\n([\w\W]*?)\n```', answer)
        diff = parsed.group(1)

    f = open("patch.diff", "w")
    print("Parsed-------------------------------------------------\n")
    print(diff)
    f.write(diff)
    f.close()

    r = Repo('./clone/')
    r.git.execute(['git', 'apply', '--reject', '--whitespace=fix', '../patch.diff'])


def parse_arguments():
    """
    Parses input arguments of the current python script
    """
    parser = argparse.ArgumentParser(
        description='Runs TED for a given git repository and perform the required task')
    required_args = parser.add_argument_group('required arguments')

    required_args.add_argument('-r', '--git-repo', type=str, help='The Git repo URL',
                                required=True)
    required_args.add_argument('-f', '--ted-flavor', type=str, help='The task to perform',
                                required=True)

    optional_args = parser.add_argument_group('optional arguments')

    optional_args.add_argument('-b', '--branch', type=str, help='Optional, The branch to use as base',
                                required=False)

    return parser.parse_args()


# -------------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()