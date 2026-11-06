# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
MIRROR = "https://maven-central.storage-download.googleapis.com/maven2/"


@pytest.mark.parametrize(
    "path,start,end,upstreams",
    [
        (
            "settings.gradle",
            "pluginManagement {",
            "plugins {",
            ("gradlePluginPortal()", "mavenCentral()"),
        ),
        (
            "settings.gradle",
            "dependencyResolutionManagement {",
            "develocity {",
            ("mavenCentral()",),
        ),
        (
            "buildSrc/build.gradle",
            "repositories {",
            "dependencies {",
            ("gradlePluginPortal()",),
        ),
    ],
)
def test_maven_mirror_precedes_upstreams(path, start, end, upstreams):
    repositories = (ROOT / path).read_text().split(start, 1)[1].split(end, 1)[0]
    assert repositories.count(MIRROR) == 1
    for upstream in upstreams:
        assert repositories.index(MIRROR) < repositories.index(upstream)
