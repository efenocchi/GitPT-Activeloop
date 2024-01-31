import re
import os
from fastapi import HTTPException
from dotenv import load_dotenv
from llama_index import download_loader
from llama_hub.github_repo import GithubRepositoryReader, GithubClient
from llama_index import VectorStoreIndex
from llama_index.vector_stores import DeepLakeVectorStore
from llama_index.storage.storage_context import StorageContext
import yaml

load_dotenv()

# Fetch and set API keys
openai_api_key = os.getenv("OPENAI_API_KEY")


# Check for OpenAI API key
if not openai_api_key:
    raise EnvironmentError("OpenAI API key not found in environment variables")


def get_validate_token(token_name):
    token = os.getenv(token_name)
    if not token:
        raise EnvironmentError(f"{token_name} not found in environment variables")
    return token


class InitiazlizeGithubService:
    def __init__(self):
        self.owner = None
        self.repo = None
        self.github_token = get_validate_token("GITHUB_TOKEN")  # Check for GitHub Token
        self.github_client = self.initialize_github_client(self.github_token)
        download_loader("GithubRepositoryReader")

    def initialize_github_client(self, github_token):
        return GithubClient(github_token)

    def parse_github_url(self, url):
        pattern = r"https://github\.com/([^/]+)/([^/]+)"
        match = re.match(pattern, url)
        return match.groups() if match else (None, None)

    def validate_owner_repo(self, owner, repo):
        if bool(owner) and bool(repo):
            self.owner = owner
            self.repo = repo
            return True

        return False

    def load_repo_data(self, owner, repo):
        if self.validate_owner_repo(owner, repo):
            loader = GithubRepositoryReader(
                self.github_client,
                owner=self.owner,
                repo=self.repo,
                filter_file_extensions=(
                    [".py", ".js", ".ts", ".md", ".ipynb"],
                    GithubRepositoryReader.FilterType.INCLUDE,
                ),
                verbose=False,
                concurrent_requests=25,
            )

            print(f"Loading {self.repo} repository by {self.owner}")

            docs = loader.load_data(branch="main")
            print("Documents uploaded:")
            for doc in docs:
                print(doc.metadata)
            print("return docs\n")
            return docs

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub URL. Please enter a valid GitHub URL",
            )


class InitiazlizeActiveloopService:
    def __init__(self):
        self.active_loop_token = get_validate_token(
            "ACTIVELOOP_TOKEN"
        )  # Check for Activeloop Token
        self.dataset_path = self.get_user_info("dataset_path")
        self.vector_store = DeepLakeVectorStore(
            dataset_path=f"hub://{self.dataset_path}",
            overwrite=True,
            runtime={"tensor_db": True},
        )

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

    def upload_to_activeloop(self, docs):
        print("uploading to activeloop")
        self.index = VectorStoreIndex.from_documents(
            docs, storage_context=self.storage_context
        )
        self.query_engine = self.index.as_query_engine()

    def get_user_info(self, user_info):
        with open("resources.yaml", "r") as file:
            yaml_data = yaml.safe_load(file)

        retrieved_info = yaml_data["info"][user_info]
        return retrieved_info
