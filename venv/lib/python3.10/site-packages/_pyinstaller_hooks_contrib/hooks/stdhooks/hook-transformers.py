from PyInstaller.utils.hooks import (
    copy_metadata,
    get_module_attribute,
    is_module_satisfies,
    logger,
)

datas = []

# At run-time, `transformers` queries the metadata of several packages to check for their presence. The list of required
# (core) packages is stored as `transformers.dependency_versions_check.pkgs_to_check_at_runtime˙. However, there is more
# comprehensive list of dependencies and their versions available in `transformers.dependency_versions_table.deps`,
# which includes non-core dependencies. Unfortunately, we cannot foresee which of those the user will actually require,
# so we collect metadata for all listed dists that are available in the build environment, in order to make them visible
# to `transformers` at run-time.
try:
    dependencies = get_module_attribute(
        'transformers.dependency_versions_table',
        'deps',
    )
except Exception:
    logger.warning(
        "hook-transformers: failed to query dependency table (transformers.dependency_versions_table.deps)!",
        exc_info=True,
    )
    dependencies = {}

for dependency_name, dependency_req in dependencies.items():
    if not is_module_satisfies(dependency_req):
        continue
    try:
        datas += copy_metadata(dependency_name)
    except Exception:
        pass

# Collect source .py files for JIT/torchscript. Requires PyInstaller >= 5.3, no-op in older versions.
module_collection_mode = 'pyz+py'
