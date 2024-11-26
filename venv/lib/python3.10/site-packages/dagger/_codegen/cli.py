import argparse
import json
import sys

import anyio
import graphql

from . import generator

parser = argparse.ArgumentParser(
    prog="python -m dagger", description="Dagger Python SDK"
)


def main():
    subparsers = parser.add_subparsers(
        title="additional commands",
        required=True,
    )
    gen_parser = subparsers.add_parser(
        "codegen",
        help="generate a Python client for the API",
    )
    gen_parser.add_argument(
        "-i",
        "--introspection",
        type=anyio.Path,
        help=(
            "path to a .json file holding the introspection result "
            "(defaults to fetching from the API)"
        ),
    )
    gen_parser.add_argument(
        "-o",
        "--output",
        type=anyio.Path,
        help=(
            "path to save the generated python module "
            "(defaults to printing it to stdout)"
        ),
    )
    args = parser.parse_args()

    # TODO: Add argument for module init.
    anyio.run(codegen, args.output, args.introspection)


async def codegen(output: anyio.Path | None, introspection: anyio.Path | None):
    code = generator.generate(await _get_schema(introspection))

    if output:
        await output.write_text(code)
        await _update_gitattributes(output)
        sys.stdout.write(f"Client generated successfully to {output}\n")
    else:
        sys.stdout.write(f"{code}\n")


async def _get_schema(path: anyio.Path | None) -> graphql.GraphQLSchema:
    if path:
        introspection = json.loads(await path.read_text())
        return graphql.build_client_schema(introspection)

    import dagger

    try:
        async with await dagger.connect() as conn:
            return await conn.session.get_schema()
    except dagger.ClientError as e:
        parser.exit(1, f"Error: {e}\n")


async def _update_gitattributes(output: anyio.Path) -> None:
    git_attrs = output.with_name(".gitattributes")
    contents = f"/{output.name} linguist-generated=true\n"

    if await git_attrs.exists():
        if contents in (text := await git_attrs.read_text()):
            return
        contents = f"{text}{contents}"

    await git_attrs.write_text(contents)
