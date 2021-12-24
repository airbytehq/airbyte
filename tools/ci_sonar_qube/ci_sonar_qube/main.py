import argparse
import sys

from .sonar_qube_api import SonarQubeApi


def main() -> int:
    parser = argparse.ArgumentParser(description='Working with SonarQube instance.')
    parser.add_argument('--host', help='SonarQube host', required=True, type=str)
    parser.add_argument('--token', help='SonarQube token', required=True, type=str)

    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument('--create_project', help='Name of future project', type=str)
    command.add_argument('--create_module', help='Name of future module project', type=str)
    command.add_argument('--remove_project', help='Name of removable project', type=str)
    command.add_argument('--remove_module', help='Name of removable module project', type=str)

    args = parser.parse_args()
    api = SonarQubeApi(host=args.host, token=args.token)
    if args.create_project or args.create_module:
        project_name = api.module2project(args.create_module) if args.create_module else args.create_project
        return 0 if api.create_project(project_name=project_name) else 1

    if args.remove_project or args.remove_module:
        project_name = api.module2project(args.remove_module) if args.remove_module else args.remove_project
        return 0 if api.remove_project(project_name=project_name) else 1

    api.logger.critical("not set any action...")
    return 1


if __name__ == '__main__':
    sys.exit(main())
