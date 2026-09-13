"""The image the registry publishes sets no environment for us.

Airbyte's CDK generates the Dockerfile; its final stage sets only
AIRBYTE_ENTRYPOINT, so `ERPL_EXTENSION_DIR` will not be there and
`LD_LIBRARY_PATH` cannot be set from Python once the process has started. The
connector therefore has to find its own extensions, and an explicit environment
variable stays as the override for development.
"""

import os
from pathlib import Path
from unittest.mock import patch

from source_sap.session import bundled_extension_dir, default_extension_dir, sidecar_extension_dir


class TestWithNoEnvironment:
    def test_prefers_the_installed_sidecar_package(self):
        # erpl-extensions ships the binaries as an ordinary dependency, so they
        # land in site-packages -- inside /usr/local, which is what the
        # generated image copies out of its builder stage.
        with patch.dict(os.environ, {}, clear=True):
            sidecar = sidecar_extension_dir()
            if sidecar is not None:
                assert default_extension_dir() == str(sidecar)
            else:
                assert default_extension_dir() == str(bundled_extension_dir())

    def test_falls_back_to_the_directory_beside_the_package(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("source_sap.session.sidecar_extension_dir", return_value=None),
        ):
            assert default_extension_dir() == str(bundled_extension_dir())

    def test_that_directory_is_inside_the_installed_package(self):
        # Must survive the image's stage copy, which keeps only /usr/local and
        # /airbyte/integration_code -- site-packages is inside the former.
        import source_sap

        assert bundled_extension_dir().is_relative_to(Path(source_sap.__file__).parent)

    def test_no_longer_points_at_a_path_the_image_will_not_have(self):
        with patch.dict(os.environ, {}, clear=True):
            assert default_extension_dir() != "/airbyte/duckdb_extensions"

    def test_an_unpopulated_sidecar_is_not_used(self):
        # A wheel built without its payload installs cleanly; using it anyway
        # would fail much later, inside DuckDB, talking about an extension.
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("source_sap.session.sidecar_extension_dir", return_value=None),
        ):
            assert default_extension_dir() == str(bundled_extension_dir())


class TestTheOverrideStillWins:
    def test_an_explicit_directory_is_used(self, tmp_path):
        with patch.dict(os.environ, {"ERPL_EXTENSION_DIR": str(tmp_path)}, clear=True):
            assert default_extension_dir() == str(tmp_path)

    def test_an_empty_value_is_not_an_override(self, tmp_path):
        with patch.dict(os.environ, {"ERPL_EXTENSION_DIR": ""}, clear=True):
            sidecar = sidecar_extension_dir()
            expected = str(sidecar) if sidecar is not None else str(bundled_extension_dir())
            assert default_extension_dir() == expected

    def test_it_is_read_per_session_not_at_import(self, tmp_path):
        # A module constant resolved at import cannot be changed by a test, nor
        # by anything that sets the variable after the connector starts.
        with patch.dict(os.environ, {"ERPL_EXTENSION_DIR": str(tmp_path)}, clear=True):
            first = default_extension_dir()
        with patch.dict(os.environ, {}, clear=True):
            second = default_extension_dir()
        assert first != second


class TestTheSharedObjectsArePreloaded:
    """`LD_LIBRARY_PATH` cannot be set from inside a running Python process.

    The ERPL RFC extension links against the SAP NetWeaver RFC SDK and ICU
    shared objects that ship beside it. In the image the registry publishes
    nothing sets a library path, so the loader has to be told about them from
    code -- an RTLD_GLOBAL preload, before DuckDB loads the extension that
    needs them.
    """

    def test_the_shared_objects_next_to_the_extensions_are_preloaded(self, tmp_path):
        from source_sap.session import preload_native_libraries

        plat = tmp_path / "v1.5.5" / "linux_amd64"
        plat.mkdir(parents=True)
        for name in ("libsapnwrfc.so", "libicuuc.so.50", "erpl_rfc.duckdb_extension"):
            (plat / name).write_bytes(b"")

        loaded = []
        preload_native_libraries(str(tmp_path), _loader=loaded.append)
        assert sorted(Path(p).name for p in loaded) == ["libicuuc.so.50", "libsapnwrfc.so"]

    def test_a_missing_directory_is_not_an_error(self, tmp_path):
        # Discovery and spec run without extensions present at all.
        from source_sap.session import preload_native_libraries

        preload_native_libraries(str(tmp_path / "nope"), _loader=lambda _: None)

    def test_a_library_that_will_not_load_does_not_fail_the_sync(self, tmp_path):
        # The real failure surfaces from DuckDB's LOAD with a usable message;
        # a preload failure on its own is not worth ending a sync for.
        from source_sap.session import preload_native_libraries

        plat = tmp_path / "v1.5.5" / "linux_amd64"
        plat.mkdir(parents=True)
        (plat / "libsapnwrfc.so").write_bytes(b"not an elf")

        def explode(_path):
            raise OSError("invalid ELF header")

        preload_native_libraries(str(tmp_path), _loader=explode)
