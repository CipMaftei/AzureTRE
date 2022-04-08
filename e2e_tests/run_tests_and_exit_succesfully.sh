#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset
# Uncomment this line to see each command for debugging (careful: this will show secrets!)
# set -o xtrace

# 1. Remove any previously run failed flag
# 2. Run pytest, but capture the exit code so we always succeed
# 3. Output a file if the tests are not successful.
results_path="/test-results"
rm -fr "${results_path}"
mkdir -p "${results_path}"
failed_file_path="/test-results/pytest_e2e_${TEST_CATEGORY}_failed"

if ! python -m pytest -m "${TEST_CATEGORY}" --verify "${IS_API_SECURED}" --junit-xml "${results_path}/pytest_e2e_${TEST_CATEGORY}.xml"; then
  echo "***************************** TESTS FAILED *****************************"
  touch "${failed_file_path}"
fi
