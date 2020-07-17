#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

pushd "${SCRIPT_DIR}/.." > /dev/null

set -e
set -x

COVERAGE_THRESHOLD=90

check_python_version() {
    python3 tools/check_python_version.py 3 6
}


echo "Create Virtualenv for Python deps ..."
function prepare_venv() {
        VIRTUALENV=$(which virtualenv)
        if [ $? -eq 1 ]
        then
            # python36 which is in CentOS does not have virtualenv binary
            VIRTUALENV=$(which virtualenv-3)
        fi

        ${VIRTUALENV} -p python3 venv && source venv/bin/activate
        if [ $? -ne 0 ]
        then
            printf "%sPython virtual environment can't be initialized%s" "${RED}" "${NORMAL}"
            exit 1
        fi

        printf "%sOK%s\n" "${GREEN}" "${NORMAL}" >&2
        pip3 install -r requirements.txt
        pip3 install -r tests/requirements.txt

}

[ "$NOVENV" == "1" ] || prepare_venv || exit 1

check_python_version

$(which pip3) install pytest-cov

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(pwd) python3 "$(which pytest)" --cov=./src --cov-config .coveragerc --cov-report term-missing --cov-fail-under=$COVERAGE_THRESHOLD -vv tests/
codecov --token=c7d85992-337d-48b1-abb4-e55429b3e9c9
printf "%stests passed%s\n\n" "${GREEN}" "${NORMAL}"

popd > /dev/null
