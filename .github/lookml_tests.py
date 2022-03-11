"""Get Data Tests. Run Data Tests"""
import looker_sdk
from looker_sdk import models
import argparse

# This script runs the data tests in a specific project.
# You can select the branch to check new changes.
# If a data test fails there will be an assertion error.


def initialize(branch, project):
    """Initialize the SDK session.

    ARGS:
    branch -- this takes the branch name we want to switch to

    project -- this takes the project name we want to run the data tests in.

    Returns:
    This returns the SDK session/token.
    """
    sdk = looker_sdk.init40()
    sdk.update_session(models.WriteApiSession(workspace_id="dev"))
    sdk.update_git_branch(project_id=project,
                          body=models.WriteGitBranch(name=branch))

    return sdk


def run_data_tests(sdk, project):
    """Run the data tests!

    Args:
    sdk -- this is the API session/token.

    project -- this is the id of the project we want to test the lookml tests in.

    Returns:
    errors -- a list of errors from failed lookml tests.
    If they all pass this list is empty.
    """
    errors = []
    results = sdk.run_lookml_test(project_id=project)
    for test in results:
        if test.errors:
            errors.append({test.test_name: test.errors})
            error_json = test.errors
            print(test.test_name + "has failed.")
            for e in error_json:
                print(e.message)
                print(e.model_id)
                print(e.sanitized_message)
    return errors


def check_tests(errors):
    """Check if tests pass.

    Args:
    errors -- a list of errors based on the results of the data tests.

    Returns:
    None
    """
    assert len(errors) == 0


def main():
    """Run Main.

    Runs the run_valiator function.

    Args: None
    Returns: None
    """

    parser = argparse.ArgumentParser(description='Run LookML Tests. Assert if any fail.')
    parser.add_argument('--project', '-p', type=str,
                        help='name of project to validate. This arg is required.')
    parser.add_argument('--branch', '-b', type=str,
                        help='Name of branch you want to validate. If ommited this will use prod.')
    args = parser.parse_args()
    project = args.project
    branch = args.branch
    sdk = initialize(branch, project)
    errors = run_data_tests(sdk, project)
    check_tests(errors)


main()
