"""Create CSV of LookML Validation."""
import looker_sdk
import pandas as pd
import argparse
from looker_sdk import error, models40

# This script will run the LookML validator on a single project and
# write the results to a CSV.
# the CSV will be the name of the project and written to the local directory.
# This takes three args: project_name, dev, branch
# project_name is required. It is the name of the project as it appears in
# the dev mode url.
# dev is optional, but accepts True or False. It can be omitted and will
# default to false. This should be used if you use the branch arg.
# branch is optional. It let's the user validate a specific branch.
# it accepts a string of the branch name. If omitted the prod branch is used.


def initialize(dev):
    """Initialize SDK.

    ARGS: Dev is the command line argument to specify if you
    want to run this in dev mode.


    RETURNS: SDK session/token
    """

    sdk = looker_sdk.init40(section="Prof")
    if dev == "True":
        sdk.update_session(body=models40.WriteApiSession(workspace_id="dev"))

    return sdk


def run_validator(sdk, project, branch):
    """Run Lookml Validator.

    This function runs the validator and writes results to a CSV.
    The CSV will be written to the local directory and the be named
    after the project.

    ARGS:
    SDK -- sdk session/token

    project -- project name to validate

    branch -- git branch name to validate

    RETURNS:
    This returns a dataframe of the validation results.
    """

    if project:
        project_name = project
        try:
            if branch:
                sdk.update_git_branch(project_id=project_name,
                                      body=models40.WriteGitBranch(name=branch)
                                      )
        except error.SDKError:
            print("check branch name")

        files = []
        models = []
        explores = []
        fields = []
        severity = []
        message = []
        try:
            validation = sdk.validate_project(project_id=project_name).errors

            for response in validation:
                files.append(response.file_path)
                models.append(response.model_id)
                explores.append(response.explore)
                fields.append(response.field_name)
                severity.append(response.severity)
                message.append(response.message)

            df = pd.DataFrame({"Files": files,
                               "Models": models,
                               "Explores": explores,
                               "Fields": fields,
                               "Severity": severity,
                               "Message": message})

            df.to_csv('%s.csv' % project_name)

            return df

        except error.SDKError:
            pass
            print("SDK ERROR, Please check project ID")
    else:
        print("No project arg passed, please rerun script with -p PROJECTID")


def assert_response(df):
    count = df.index
    rows = len(count)
    print(rows)
    assert rows == 0


def main():
    """Run Main.

    Runs the run_valiator function.

    Args: None
    Returns: None
    """
    parser = argparse.ArgumentParser(description='Validate LookML and write the result to a CSV')
    parser.add_argument('--project', '-p', type=str,
                        help='name of project to validate. This arg is required.')
    parser.add_argument('--dev', '-d', type=str,
                        help='If you want to run validation in prod or dev. Accepts True or False.')
    parser.add_argument('--branch', '-b', type=str,
                        help='Name of branch you want to validate. If ommited this will use prod.')
    args = parser.parse_args()
    project = args.project
    dev = args.dev
    branch = args.branch
    sdk = initialize(dev)
    df = run_validator(sdk, project, branch)
    assert_response(df)


main()
