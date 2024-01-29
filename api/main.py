import textwrap
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from external_services import InitiazlizeGithubService, InitiazlizeActiveloopService

# Load environment variables
load_dotenv()


app = FastAPI()


class GitHubRepoRequest(BaseModel):
    githubRepoUrl: str


class UserCodeRequest(BaseModel):
    userCode: str


@app.post("/upload")
async def scrape_and_upload_to_activeloop(repo_request: GitHubRepoRequest):
    # Add logic to scrape and upload to ActiveLoop
    # Example: Scrape GitHub repo and upload to ActiveLoop
    # Implement your scraping and upload logic here
    github_service = InitiazlizeGithubService()
    activeloop_service = InitiazlizeActiveloopService()

    print(f"repo from user: {repo_request.githubRepoUrl}")

    owner, repo = github_service.parse_github_url(repo_request.githubRepoUrl)
    docs = github_service.load_repo_data(owner, repo)
    activeloop_service.upload_to_activeloop(docs)

    return {"status": "success", "message": "Repo processed successfully"}


@app.post("/retrieve")
async def find_similar_code_and_explain(code_request: UserCodeRequest):
    # Add logic to find similar code and provide explanations or improvements
    # Example: Search in ActiveLoop DB
    # Implement your search and analysis logic here
    activeloop_service = InitiazlizeActiveloopService()

    print(f"code from user: {code_request.userCode}")

    # intro_question = "What is the repository about?"
    intro_question = code_request.userCode
    print(f"Test question: {intro_question}")
    print("=" * 50)

    answer = activeloop_service.query_engine.query(intro_question)
    print(f"Answer: {textwrap.fill(str(answer), 100)} \n")

    return {
        "answer": answer,
    }
