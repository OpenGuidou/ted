import os
import unittest

from git import Repo
import requests
import shutil
from helpers.GitHelper import GitHelper
from unittest import mock


# -------------------------------------------------------------------------------------------
# Mocks used in the below unit test class
# -------------------------------------------------------------------------------------------
def mocked_pull_request_failure(*args, **kwargs):
    """
    Mock function to mimic a failure to create a pull request
    """
    raise requests.exceptions.HTTPError

def mocked_pull_request_success(*args, **kwargs):
    """
    Mock function to mimic a success to create a pull request
    """
    response = requests.Response()
    response.status_code = 200

    return response

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def mocked_git_repository_clone(*args, **kwargs):
    if os.path.isdir(args[0]):
        shutil.rmtree(args[0], onerror=onerror)
    os.makedirs(args[0])

    with open(os.path.join(args[0], "test_file.txt"), "w") as file:
        file.write("Test text goes here")

    r = Repo.init(args[0])
    r.git.add(all=True)
    r.remote = mock.MagicMock()

    return r

# -------------------------------------------------------------------------------------------
# Unit test class
# -------------------------------------------------------------------------------------------
class TestGitHelper(unittest.TestCase):

    # Mock some methods. The mock object is passed in to our test case method.
    @mock.patch('helpers.GitHelper.requests.post', side_effect=mocked_pull_request_failure)
    def test_create_pull_request_ko(self, mock_requests_post):
        git_helper = GitHelper()
        repository = "repository"
        title = "title"
        description = "description"
        head_branch = "head_branch"
        base_branch = "base_branch"
        git_token = "git_token"
        self.assertRaises(requests.exceptions.HTTPError,
                          lambda: git_helper.create_pull_request(repository, title, description, head_branch,
                                                                 base_branch, git_token))
        expected_headers = {
            "Authorization": "token git_token",
            "Content-Type": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.assertIn(mock.call("https://api.github.com/repos/repository/pulls",
                                headers=expected_headers,
                                data="{\"title\": \"title\", \"body\": \"description\", "
                                     "\"head\": \"head_branch\", \"base\": \"base_branch\"}"),
                      mock_requests_post.call_args_list)

    # Mock some methods. The mock object is passed in to our test case method.
    @mock.patch('helpers.GitHelper.requests.post', side_effect=mocked_pull_request_success)
    def test_create_pull_request_ok(self, mock_requests_post):
        git_helper = GitHelper()
        repository = "repository"
        title = "title"
        description = "description"
        head_branch = "head_branch"
        base_branch = "base_branch"
        git_token = "git_token"
        git_helper.create_pull_request(repository, title, description, head_branch, base_branch, git_token)
        expected_headers = {
            "Authorization": "token git_token",
            "Content-Type": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.assertIn(mock.call("https://api.github.com/repos/repository/pulls",
                                headers=expected_headers,
                                data="{\"title\": \"title\", \"body\": \"description\", "
                                     "\"head\": \"head_branch\", \"base\": \"base_branch\"}"),
                      mock_requests_post.call_args_list)

    # Mock some methods. The mock object is passed in to our test case method.
    @mock.patch('helpers.GitHelper.Repo', side_effect=mocked_git_repository_clone)
    def test_push_changes_in_pull_request(self, mock_git_repo):
        git_helper = GitHelper()
        repository = "repository"
        message = "message"
        target_branch = "target_branch"
        head_branch = "head_branch"
        git_token = "git_token"
        clone_path = "clone_path"
        git_helper.push_changes_in_pull_request(repository, message, target_branch, head_branch, git_token, clone_path)

        self.assertIn(mock.call(clone_path), mock_git_repo.call_args_list)

# -------------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
