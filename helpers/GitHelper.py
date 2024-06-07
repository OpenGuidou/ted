import json
import requests

from git import Repo

class GitHelper(object):
    """
    Helper class for GIT
    """

    def create_pull_request(self, repository, title, description, head_branch, base_branch, git_token):
        """Creates the pull request for the head_branch against the base_branch"""
        git_pulls_api = "https://api.github.com/repos/{repository}/pulls".format(repository=repository)

        headers = {
            "Authorization": "token {0}".format(git_token),
            "Content-Type": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        payload = {
            "title": title,
            "body": description,
            "head": head_branch,
            "base": base_branch,
        }

        try:
            r = requests.post(
                git_pulls_api,
                headers=headers,
                data=json.dumps(payload))
            if not r.ok:
                print("Request Failed: {0}".format(r.text))
        except requests.exceptions.RequestException as e:
            print("Request Failed: {0}".format(e))
            raise e

    def push_changes_in_pull_request(self, repository, message, target_branch, head_branch, token, clone_path):

        r = Repo(clone_path)
        r.git.execute(['git', 'config', '--global', '--add', 'safe.directory', clone_path])
        r.git.execute(['git', 'checkout', '-b', target_branch])
        files_to_add = r.git.execute(
            ['git', 'ls-files', '--others', '--exclude-standard', 'grep', '\.java', '|', 'grep', 'src/test'])
        r.git.execute(['git', 'add', files_to_add])
        r.git.commit('-am', message)
        origin = r.remote(name='origin')
        origin.push(target_branch)

        self.create_pull_request(repository, message, '', target_branch, head_branch, token)