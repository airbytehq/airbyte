import json
import os
import sys

backend_spec = sys.argv[1]
backend_obj = sys.argv[2] if len(sys.argv) >= 3 else None
backend_paths = sys.argv[3].split(os.path.pathsep) if len(sys.argv) >= 4 else []

sys.path[:0] = backend_paths

backend = __import__(backend_spec, fromlist=["_trash"])
if backend_obj:
    backend = getattr(backend, backend_obj)

try:
    for_build_requires = backend.get_requires_for_build_sdist(None)
except AttributeError:
    # PEP 517 states that get_requires_for_build_sdist is optional for a build
    # backend object. When the backend object omits it, the default
    # implementation must be equivalent to return []
    for_build_requires = []

output = json.dumps(for_build_requires)
print(output)
