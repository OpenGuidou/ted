import json
import requests

from git import Repo

class GitHelper(object):
    """
    Helper class for GIT
    """

    def create_pull_request(self, repository, title, description, head_branch, base_branch, git_token):
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

    def push_changes_in_pull_request(self, repository, message, target_branch, head_branch, token, clone_path):

        r = Repo(clone_path)
        r.git.execute(['git', 'config', '--global', '--add', 'safe.directory', clone_path])
        r.git.execute(['git', 'checkout', '-b', target_branch])
        r.git.commit('-am', message)
        r.git.push('origin', target_branch)

        self.create_pull_request(repository, message, '', target_branch, head_branch, token)