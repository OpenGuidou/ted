import os
import argparse
from dotenv import load_dotenv

from services.UnitTestsGenerator import UnitTestsGenerator
from services.Python2To3Migrator import Python2To3Migrator
from git import *
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.document_loaders import GitLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def main():

    """
    Main function of this script. Promotes chart changes from one repository branch to another, given a source commit.
    """
    # Parses input arguments, initializes various local variables and perform basic checks on input parameters
    arguments = parse_arguments()

    git_url = arguments.git_repo
    branch = arguments.branch
    ted_flavor = arguments.ted_flavor

    load_dotenv()

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

    llm = AzureChatOpenAI(
        deployment_name=os.getenv('GPT_DEPLOYMENT_NAME'),
        #temperature=0.5,
    )

    output_parser = StrOutputParser()

    # Check if git_url exists
    clone_path = None
    if git_url:
        print(f"Loaded clones repository from URL: {git_url}")
        clone_path="./clone/"
        loader = GitLoader(
            clone_url=git_url,
            repo_path=clone_path,
            branch=branch,
            file_filter=lambda file_path: filter_files(file_path, generator.getFileExtensions())
        )
    else:
        print(f"Loader uses from github workspace")
        clone_path=os.getenv('GITHUB_WORKSPACE')
        loader = DirectoryLoader(
            path=clone_path,
            glob=generator.getFileGlob(), # @TODO Find a way to use glob with extensions: "**/*{" +",".join(generator.getFileExtensions()) + "}",
            show_progress=True,
            loader_cls=TextLoader
        )

    textFormat = generator.getTextFormat()

    print(f"Load documents")
    docs = loader.load()

    # if zero docs stop
    if len(docs) == 0:
        print("No documents found.")
        return
    
    print("Using language splitter {}.".format(textFormat))
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=textFormat ,chunk_size=2000, chunk_overlap=200
    )

    print("Split documents")
    texts = text_splitter.split_documents(docs)

    print("Create embeddings and vectorstore")
    embedding = AzureOpenAIEmbeddings(
        # keys and endpoint are read from the .env file
        openai_api_version=os.getenv('OPENAI_API_VERSION'),
        deployment=os.getenv('EMBEDDING_DEPLOYMENT_NAME'),
    )
    vectorstore = FAISS.from_documents(
        texts, embedding=embedding
    )
    retriever = vectorstore.as_retriever()

    print(f"Run generation")
    generator.runGeneration(retriever, llm, output_parser, clone_path)    

def filter_files(file_path, extensions):
    """
    Filters files based on the given extensions
    """
    for extension in extensions:
        if file_path.endswith(extension):
            return True
    return False

def parse_arguments():
    """
    Parses input arguments of the current python script
    """
    parser = argparse.ArgumentParser(
        description='Runs TED for a given git repository and perform the required task')
    required_args = parser.add_argument_group('required arguments')

    required_args.add_argument('-f', '--ted-flavor', type=str, help='The task to perform',
                                required=True)

    optional_args = parser.add_argument_group('optional arguments')

    required_args.add_argument('-r', '--git-repo', type=str, help='The Git repo URL',
                                required=False)
    
    optional_args.add_argument('-b', '--branch', type=str, help='Optional, The branch to use as base',
                                required=False)

    return parser.parse_args()


# -------------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()