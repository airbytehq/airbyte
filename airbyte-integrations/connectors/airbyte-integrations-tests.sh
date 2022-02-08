#! /usr/bin/env bash

SOURCES=($(find ./ -maxdepth 1 -type d -name 'source-*'))
DESTINATIONS=($(find ./ -maxdepth 1 -type d -name 'destination-*'))

echo
SOURCES_WITHOUT_ACCEPTANCE_TESTS=()
SOURCES_WITHOUT_UNIT_TESTS=()
SOURCES_WITHOUT_INTEGRATION_TESTS=()
echo "Checking ${#SOURCES[@]} sources"
for source in "${SOURCES[@]}"; do
  # echo "$source"
  if [ ! -f "${source}/acceptance-test-config.yml" ]; then
    SOURCES_WITHOUT_ACCEPTANCE_TESTS+=("${source}")
  fi

  # Determine language of connector.
  # Python
  if [ -f "${source}/setup.py" ]; then
    # Python unit tests tend to be in this path
    if [ ! -d "${source}/unit_tests" ]; then
      SOURCES_WITHOUT_UNIT_TESTS+=("${source}")
    fi

    # Python integration tests tend to be in this path
    if [ ! -d "${source}/integration_tests" ]; then
      SOURCES_WITHOUT_INTEGRATION_TESTS+=("${source}")
    fi

  # Java
  elif [ -d "${source}/src" ]; then
    # Some Java connectors have additional integration tests in this path
    if [ ! -d "${source}/src/test-integration" ]; then
      SOURCES_WITHOUT_INTEGRATION_TESTS+=("${source}")
    fi

    # Seems like this is where Java unit tests go?
    if [ ! -d "${source}/src/test" ]; then
      SOURCES_WITHOUT_UNIT_TESTS+=("${source}")
    fi
  fi
done

echo
echo "The following ${#SOURCES_WITHOUT_ACCEPTANCE_TESTS[@]} sources do not implement acceptance tests"
for source in "${SOURCES_WITHOUT_ACCEPTANCE_TESTS[@]}"; do
  echo "$source"
  if [[ -n "${VERBOSE}" ]]; then
    ls -l "$source" | awk '{print $9}'
    echo
  fi
done

echo
echo "The following ${#SOURCES_WITHOUT_UNIT_TESTS[@]} sources do not implement unit tests"
for source in "${SOURCES_WITHOUT_UNIT_TESTS[@]}"; do
  echo "$source"
  if [[ -n "${VERBOSE}" ]]; then
    ls -l "$source" | awk '{print $9}'
    echo
  fi
done

echo
echo "The following ${#SOURCES_WITHOUT_INTEGRATION_TESTS[@]} sources do not implement additional integration tests"
for source in "${SOURCES_WITHOUT_INTEGRATION_TESTS[@]}"; do
  echo "$source"
  if [[ -n "${VERBOSE}" ]]; then
    ls -l "$source" | awk '{print $9}'
    echo
  fi
done

echo
DESTINATIONS_WITHOUT_UNIT_TESTS=()
DESTINATIONS_WITHOUT_INTEGRATION_TESTS=()
echo "Checking ${#DESTINATIONS[@]} destinations"
for destination in "${DESTINATIONS[@]}"; do
  # echo "$destination"

  # Determine language of connector.
  # Python
  if [ -f "${destination}/setup.py" ]; then
    # Python unit tests tend to be in this path
    if [ ! -d "${destination}/unit_tests" ]; then
      DESTINATIONS_WITHOUT_UNIT_TESTS+=("${destination}")
    fi

    # Python integration tests tend to be in this path
    if [ ! -d "${destination}/integration_tests" ]; then
      DESTINATIONS_WITHOUT_INTEGRATION_TESTS+=("${destination}")
    fi

  # Java
  elif [ -d "${destination}/src" ]; then
    # Some Java connectors have additional integration tests in this path
    if [ ! -d "${destination}/src/test-integration" ]; then
      DESTINATIONS_WITHOUT_INTEGRATION_TESTS+=("${destination}")
    fi

    # Seems like this is where Java unit tests go?
    if [ ! -d "${destination}/src/test" ]; then
      DESTINATIONS_WITHOUT_UNIT_TESTS+=("${destination}")
    fi
  fi
done


echo
echo "The following ${#DESTINATIONS_WITHOUT_UNIT_TESTS[@]} destinations do not implement unit tests"
for destination in "${DESTINATIONS_WITHOUT_UNIT_TESTS[@]}"; do
  echo "$destination"
  if [[ -n "${VERBOSE}" ]]; then
    ls -l "$destination" | awk '{print $9}'
    echo
  fi
done

echo
echo "The following ${#DESTINATIONS_WITHOUT_INTEGRATION_TESTS[@]} destinations do not implement additional integration tests"
for destination in "${DESTINATIONS_WITHOUT_INTEGRATION_TESTS[@]}"; do
  echo "$destination"
  if [[ -n "${VERBOSE}" ]]; then
    ls -l "$destination" | awk '{print $9}'
    echo
  fi
done
