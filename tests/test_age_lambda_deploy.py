"""Tests for the Lambda deployment seam in age_lambda.py.

Run with: python -m unittest discover -s tests
These tests use only the standard library and do not contact AWS.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import age_lambda  # noqa: E402


class DeployLambdaFunctionsTest(unittest.TestCase):
    def test_deploy_script_path_exists_in_repo(self):
        self.assertTrue(os.path.isfile(age_lambda.LAMBDA_DEPLOY_SCRIPT))
        self.assertEqual(
            os.path.basename(os.path.dirname(age_lambda.LAMBDA_DEPLOY_SCRIPT)),
            "lambda_functions",
        )

    def test_runs_deploy_script_with_current_interpreter_from_any_cwd(self):
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            try:
                with mock.patch.object(age_lambda.subprocess, "run") as run:
                    age_lambda.deploy_lambda_functions()
                # No credentials file is written as a side effect.
                self.assertEqual(os.listdir(tmp), [])
            finally:
                os.chdir(original_cwd)

        run.assert_called_once_with(
            [sys.executable, age_lambda.LAMBDA_DEPLOY_SCRIPT], check=True
        )

    def test_deploy_failure_is_reported_as_runtime_error(self):
        error = subprocess.CalledProcessError(1, ["deploy.py"])
        with mock.patch.object(age_lambda.subprocess, "run", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "Failed to deploy Lambda functions"):
                age_lambda.deploy_lambda_functions()


if __name__ == "__main__":
    unittest.main()
