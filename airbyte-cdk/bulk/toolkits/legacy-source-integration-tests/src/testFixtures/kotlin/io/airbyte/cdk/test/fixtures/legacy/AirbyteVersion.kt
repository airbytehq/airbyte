/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

/**
 * The AirbyteVersion identifies the version of the database used internally by Airbyte services.
 */
class AirbyteVersion : Version {
    constructor(version: String) : super(version)

    constructor(major: String?, minor: String?, patch: String?) : super(major, minor, patch)

    override fun toString(): String {
        return "AirbyteVersion{" +
            "version='" +
            version +
            '\'' +
            ", major='" +
            this.major +
            '\'' +
            ", minor='" +
            minor +
            '\'' +
            ", patch='" +
            patch +
            '\'' +
            '}'
    }

    companion object {
        const val AIRBYTE_VERSION_KEY_NAME: String = "airbyte_version"

        @Throws(IllegalStateException::class)
        fun assertIsCompatible(version1: AirbyteVersion, version2: AirbyteVersion) {
            check(Version.Companion.isCompatible(version1, version2)) {
                getErrorMessage(version1, version2)
            }
        }

        fun getErrorMessage(version1: AirbyteVersion, version2: AirbyteVersion): String {
            return String.format(
                """
                        Version mismatch between %s and %s.
                        Please upgrade or reset your Airbyte Database, see more at https://docs.airbyte.io/operator-guides/upgrading-airbyte
                        """.trimIndent(),
                version1.serialize(),
                version2.serialize()
            )
        }

        fun versionWithoutPatch(airbyteVersion: AirbyteVersion): AirbyteVersion {
            val versionWithoutPatch =
                ("" +
                    airbyteVersion.major +
                    "." +
                    airbyteVersion.minor +
                    ".0-" +
                    airbyteVersion
                        .serialize()
                        .replace("\n", "")
                        .trim()
                        .split("-".toRegex())
                        .dropLastWhile { it.isEmpty() }
                        .toTypedArray()[1])
            return AirbyteVersion(versionWithoutPatch)
        }

        fun versionWithoutPatch(airbyteVersion: String): AirbyteVersion {
            return versionWithoutPatch(AirbyteVersion(airbyteVersion))
        }
    }
}
