#!/bin/bash

set -e
set -x

COVERAGE_THRESHOLD=90

check_python_version() {
    python3 tools/check_python_version.py 3 6
}


echo "Create Virtualenv for Python deps ..."
function prepare_venv() {
        # we want tests to run on python3.6
        printf 'checking alias `python3.6` ... ' >&2
        PYTHON=$(which python3.6 2> /dev/null)
        if [ "$?" -ne "0" ]; then
                printf "%sNOT FOUND%s\n" "${YELLOW}" "${NORMAL}" >&2

                printf 'checking alias `python3` ... ' >&2
                PYTHON=$(which python3 2> /dev/null)

                let ec=$?
                [ "$ec" -ne "0" ] && printf "${RED} NOT FOUND ${NORMAL}\n" && return $ec
        fi

        printf "%sOK%s\n" "${GREEN}" "${NORMAL}" >&2

        ${PYTHON} -m venv "venv" && source venv/bin/activate
        pip install -U pip
        python3 "$(which pip3)" install -r requirements.txt
        python3 "$(which pip3)" install -r tests/requirements.txt

}

[ "$NOVENV" == "1" ] || prepare_venv || exit 1

check_python_version

$(which pip3) install pytest-cov

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(pwd) python3 "$(which pytest)" --cov=. --cov-config .coveragerc --cov-report term-missing --cov-fail-under=$COVERAGE_THRESHOLD -vv tests/
codecov --token=c7d85992-337d-48b1-abb4-e55429b3e9c9
printf "%stests passed%s\n\n" "${GREEN}" "${NORMAL}"
