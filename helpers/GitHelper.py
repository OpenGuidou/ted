import json
import requests

from git import *

def create_pull_request(repository, title, description, head_branch, base_branch, git_token):
    """Creates the pull request for the head_branch against the base_branch"""
    git_pulls_api = "https://github.com/api/v3/repos/{repository}/pulls".format(repository)
    
    headers = {
        "Authorization": "token {0}".format(git_token),
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "body": description,
        "head": head_branch,
        "base": base_branch,
    }

    r = requests.post(
        git_pulls_api,
        headers=headers,
        data=json.dumps(payload))

    if not r.ok:
        print("Request Failed: {0}".format(r.text))

def pushChangesInPullRequest(repository, message, targetBranch, headBranch, token):

    r = Repo('./clone/')
    r.git.execute(['git', 'checkout', '-b', targetBranch])
    r.git.commit('-am', message)
    r.git.push('origin', targetBranch)
    
    create_pull_request(repository, message, '', targetBranch, headBranch, token)