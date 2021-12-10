#!/bin/python
import docker
import os
import pathlib
import sys
from docker.client import DockerClient
from docker.models.images import Image


def build(client: DockerClient, image_name: str, code_folder: str) -> Image:
    """Tries to build a image"""
    # generate Dockerfile
    dockerfile = pathlib.Path(code_folder) / "Dockerfile"
    with open(dockerfile, "w") as file:
        file.write(f"FROM {image_name}\n")
        file.write(f"COPY ./ /data\n")
        file.write(f'ENTRYPOINT ["bash", "/data/py_script.sh"]\n')
    # raise Exception(open(dockerfile, "r").read())
    image, _ = client.images.build(
        path=code_folder,
        tag=image_name + ".test"
    )
    return image


def run(client: DockerClient, image: Image, cmd: str) -> int:
    volumes = {
        "/var/run/docker.sock": {'bind': '/var/run/docker.sock', 'mode': 'rw'},
    }
    container = client.containers.run(
        image=image, command=cmd,
        detach=True, working_dir="/data",
        volumes=volumes, auto_remove=True
    )
    for line in container.logs(
            stdout=True, stderr=True,
            stream=True, follow=True,
    ):
        line = line.strip().decode().replace("\\\\n", "\n")
        print(line)
    exit_status = container.wait()
    print(f"Result: {exit_status}")
    return exit_status["StatusCode"]


def main() -> int:
    client = docker.from_env()
    image_name = sys.argv[1]
    code_folder = sys.argv[2]
    test_args = " ".join(sys.argv[3:])
    image = build(client, image_name, code_folder)
    try:
        return run(client, image, test_args)
    finally:
        client.images.remove(image.id, force=True)


sys.exit(main())
