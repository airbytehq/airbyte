#!/usr/bin/env python3
import os
import sys
import subprocess
from importlib.resources import files

def main():
    if len(sys.argv) < 2:
        print("Usage: python wrapper_script.py <command> [additional_args...]")
        print("Commands: check, discover, read, write, spec")
        sys.exit(1)

    command = sys.argv[1]
    valid_commands = ['check', 'discover', 'read', 'write', 'spec']

    if command not in valid_commands:
        print(f"Error: Invalid command '{command}'")
        print(f"Valid commands: {', '.join(valid_commands)}")
        sys.exit(1)

    additional_args = sys.argv[2:]


    # Java connectors expect the first argument to be the command, prefixed with '--'.
    bash_args = [f"--{command}"] + additional_args

    env_vars = os.environ.copy()
    env_vars['JAVA_HOME'] = files("${JAVA_RUNTIME_PACKAGE_NAME}").joinpath("${JAVA_RUNTIME_DIR_NAME}")

    try:
        script_path = files("${CONNECTOR_PACKAGE_NAME}").joinpath("bin/${CONNECTOR_TYPE}-${CONNECTOR_NAME}")
        result = subprocess.run([script_path] + bash_args, check=True, env=env_vars)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: bash script '${CONNECTOR_TYPE}-${CONNECTOR_NAME}' not found")
        sys.exit(1)

if __name__ == "__main__":
    main()
