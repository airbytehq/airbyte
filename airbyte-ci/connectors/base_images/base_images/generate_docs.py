#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from jinja2 import Environment, FileSystemLoader

from .registries import PYTHON_REGISTRY

env = Environment(loader=FileSystemLoader("base_images/templates"))


def main():
    template = env.get_template("README.md.j2")
    rendered_template = template.render({"registries": [PYTHON_REGISTRY]})
    with open("README.md", "w") as readme:
        readme.write(rendered_template)
