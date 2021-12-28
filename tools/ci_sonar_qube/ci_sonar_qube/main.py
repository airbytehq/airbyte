import argparse
import sys

from .sonar_qube_api import SonarQubeApi


def main() -> int:
    need_print_key = "--print_key" in sys.argv
    parser = argparse.ArgumentParser(description='Working with SonarQube instance.')
    parser.add_argument('--host', help='SonarQube host', required=not need_print_key, type=str)
    parser.add_argument('--token', help='SonarQube token', required=not need_print_key, type=str)
    parser.add_argument('--pr', help='PR unique name. Example: airbyte/1231', type=str, default=None)

    name_value = parser.add_mutually_exclusive_group(required=True)
    name_value.add_argument('--project', help='Name of future project', type=str)
    name_value.add_argument('--module', help='Name of future module project', type=str)

    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument('--print_key', help='Return a generate SonarQube key', action="store_true")
    command.add_argument('--create', help='create a project', action="store_true")
    command.add_argument('--remove', help='remove project', action="store_true")

    args = parser.parse_args()
    api = SonarQubeApi(host=args.host, token=args.token, pr_name=args.pr)

    project_name = api.module2project(args.module) if args.module else args.project

    if args.create:
        return 0 if api.create_project(project_name=project_name) else 1
    elif args.remove:
        return 0 if api.remove_project(project_name=project_name) else 1
    elif args.print_key:
        data = api.prepare_project_settings(project_name)
        print(data["project"], file=sys.stdout)
        return 0
    api.logger.critical("not set any action...")
    return 1


if __name__ == '__main__':
    sys.exit(main())
