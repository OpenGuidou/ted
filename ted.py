import os
import argparse
from uuid import uuid1
from dotenv import load_dotenv

from helpers.GitHelper import GitHelper
from services.UnitTestsGenerator import UnitTestsGenerator
from services.Python2To3Migrator import Python2To3Migrator
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
    github_token = os.getenv('GITHUB_TOKEN')
    branch = arguments.git_branch
    push = arguments.push
    github_repository = arguments.github_repository
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
            print("Python 2 to 3 migration.")
            generator = Python2To3Migrator()
        case _:
            print("Unsupported ted flavor.")
            return

    llm = AzureChatOpenAI(
         deployment_name=os.getenv('GPT_DEPLOYMENT_NAME'),
         # temperature=0.5,
     )
    
    output_parser = StrOutputParser()
    
     # Check if git_url exists
    clone_path = None
    if git_url:
        print(f"Loaded clones repository from URL: {git_url}")
        clone_path = "./clone/"
        loader = GitLoader(
            clone_url=git_url,
            repo_path=clone_path,
            branch=branch,
            file_filter=lambda file_path: filter_files(file_path, generator.get_file_extensions())
        )
    else:
        clone_path = os.getenv('GITHUB_WORKSPACE')
        print(f"Loader uses from github workspace: {clone_path}")
        loader = DirectoryLoader(
            path=clone_path,
            glob=generator.get_file_glob(),
            # @TODO Find a way to use glob with extensions: "**/*{" +",".join(generator.getFileExtensions()) + "}",
            show_progress=True,
            loader_cls=TextLoader
        )

    text_format = generator.get_text_format()

    print("Load documents")
    docs = loader.load()

    # if zero docs stop
    if len(docs) == 0:
        print("No documents found.")
        return

    print("Using language splitter {}.".format(text_format))
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=text_format, chunk_size=2000, chunk_overlap=200
    )

    print("Split documents")
    texts = text_splitter.split_documents(docs)

    print("Create embeddings and vector store")
    embedding = AzureOpenAIEmbeddings(
        # keys and endpoint are read from the .env file
        openai_api_version=os.getenv('OPENAI_API_VERSION'),
        deployment=os.getenv('EMBEDDING_DEPLOYMENT_NAME'),
    )
    vector_store = FAISS.from_documents(
        texts, embedding=embedding
    )
    retriever = vector_store.as_retriever()

    print("😀 Run generation")
    generator.run_generation(retriever, llm, output_parser, clone_path)

    if (push and github_repository and branch and github_token):
        print("😎👌🔥 Push changes in pull request")
        GitHelper().push_changes_in_pull_request(github_repository, "ted: suggestions",
                                                 "feat/ted_suggestions-" + str(uuid1()), branch, github_token,
                                                 clone_path)


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

    required_args.add_argument('-r', '--git_repo', type=str, help='The Git repo URL',
                               required=False)

    optional_args.add_argument('-b', '--git_branch', type=str, help='Optional, The branch to use as base',
                               required=False)

    optional_args.add_argument('-ghr', '--github_repository', type=str, help='Optional, Github repository (owner/repo)',
                               required=False)

    optional_args.add_argument('-p', '--push', type=str, help='Optional, Github repository (owner/repo)',
                               required=False)

    return parser.parse_args()


# -------------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
 