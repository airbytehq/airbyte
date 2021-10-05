import os
import sys

from .source import SourceFileSecure

current_dir = os.path.dirname(os.path.abspath(__file__))

parent_source_local = os.path.join(current_dir, "../../source-file/source_file")
parent_source_docker = os.path.join(current_dir, "../source_file")
if os.path.isdir(parent_source_docker):
    sys.path.append(parent_source_docker)
elif os.path.isdir(parent_source_local):
    sys.path.append(parent_source_local)
else:
    raise RuntimeError("not found parent source folder")

__all__ = ["SourceFileSecure"]
