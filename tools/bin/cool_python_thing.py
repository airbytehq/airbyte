#!/usr/bin/python3

import os
import sys

# get current directory
path = os.getcwd()
print(f"Current Directory is {path}")

# prints parent directory
parent_dir = os.path.abspath(os.path.join(path, os.pardir))
print(f"parent Directory is {parent_dir}")

# prints module path
module_path = os.path.abspath(os.path.join(parent_dir, "python_lib"))
print(f"module path is {module_path}")


sys.path.append(module_path)


from immma_module import Topher_class as Better_named_class


if __name__ == "__main__":

  obj = Better_named_class()
  print(obj.instance_method(10))
