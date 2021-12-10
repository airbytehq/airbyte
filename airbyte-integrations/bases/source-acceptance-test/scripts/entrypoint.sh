#!/bin/bash

POSITIONAL=("tests")
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -c|--acceptance-test-config)
      CONNECTOR_FOLDER="$2"
      shift # past argument
      shift # past value
      ;;
    -a|--all-tests)
      ALL_TESTS="1"
      shift # past argument
      ;;
    *) # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL[@]}" # restore positional parameters


function run_default_tests() {
  python -m pytest -p source_acceptance_test.plugin --acceptance-test-config ${CONNECTOR_FOLDER} $@
  return $?
}

if [ -z ${ALL_TESTS} ]; then
  echo "run default logic... if you want to run all tests (unit_tests, flake8 etc), you need to add --all-tests"
  run_default_tests
  exit $?
fi

echo "CONNECTOR FOLDER  = ${CONNECTOR_FOLDER}"
if [ -z ${CONNECTOR_FOLDER} ]; then
  echo "option --acceptance-test-config is required!!"
  exit 1
fi
if [ ! -d ${CONNECTOR_FOLDER} ]; then
  echo "not found the folder ${CONNECTOR_FOLDER}"
  exit 1
fi

CONFIG_FILE="${CONNECTOR_FOLDER}/acceptance-test-config.yml"
echo "try to find a config file: ${CONFIG_FILE}"
if [ ! -f ${CONFIG_FILE} ]; then
  echo "not found ${CONFIG_FILE}"
  run_default_tests
  exit $?
fi

PY_SETUP_FILE="${CONNECTOR_FOLDER}/setup.py"
echo "try to find a setup.py file: ${PY_SETUP_FILE}"
if [ ! -f ${PY_SETUP_FILE} ]; then
  echo "not found ${PY_SETUP_FILE} and this is not Python connector ${PY_SETUP_FILE}..."
  echo "run default logic"
  unset PY_SETUP_FILE
  run_default_tests
  exit $?
fi

SOURCE_IMAGE=$(cat ${CONFIG_FILE} | grep "connector_image" | head -n 1 | cut -d: -f2-)
echo "found image name: ${SOURCE_IMAGE}..."

# copy payload folders only
TMP_FOLDER="/temp_input_folder/"
mkdir -p "${TMP_FOLDER}/code_folder/" "${TMP_FOLDER}/source_acceptance_test/"
for d in ${CONNECTOR_FOLDER}/*; do
 if [ $d == "${CONNECTOR_FOLDER}/.venv" ] || \
    [ $d == "${CONNECTOR_FOLDER}/build" ] || \
    [ $d == "${CONNECTOR_FOLDER}/htmlcov" ] || \
    [ $d == "${CONNECTOR_FOLDER}/acceptance_tests_logs" ]; then
   continue
 fi
 cp -rf ${d} ${TMP_FOLDER}/code_folder/
done

cp -rf  ./* "${TMP_FOLDER}/source_acceptance_test/"
cp /scripts/py_script.sh ${TMP_FOLDER}
# run docker by python because docker-cli util has a big size (+- 100Mb)
python /scripts/run_docker.py $SOURCE_IMAGE ${TMP_FOLDER} "$@"
exit $?
