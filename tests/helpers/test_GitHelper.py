import unittest
import requests
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

# -------------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
