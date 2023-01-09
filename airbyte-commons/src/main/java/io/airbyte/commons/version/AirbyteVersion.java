/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

/**
 * The AirbyteVersion identifies the version of the database used internally by Airbyte services.
 */
public class AirbyteVersion extends Version {

  public static final String AIRBYTE_VERSION_KEY_NAME = "airbyte_version";

  public AirbyteVersion(final String version) {
    super(version);
  }

  public AirbyteVersion(final String major, final String minor, final String patch) {
    super(major, minor, patch);
  }

  public static void assertIsCompatible(final AirbyteVersion version1, final AirbyteVersion version2) throws IllegalStateException {
    if (!isCompatible(version1, version2)) {
      throw new IllegalStateException(getErrorMessage(version1, version2));
    }
  }

  public static String getErrorMessage(final AirbyteVersion version1, final AirbyteVersion version2) {
    return String.format(
        "Version mismatch between %s and %s.\n" +
            "Please upgrade or reset your Airbyte Database, see more at https://docs.airbyte.io/operator-guides/upgrading-airbyte",
        version1.serialize(), version2.serialize());
  }

  @Override
  public String toString() {
    return "AirbyteVersion{" +
        "version='" + version + '\'' +
        ", major='" + major + '\'' +
        ", minor='" + minor + '\'' +
        ", patch='" + patch + '\'' +
        '}';
  }

  public static AirbyteVersion versionWithoutPatch(final AirbyteVersion airbyteVersion) {
    final String versionWithoutPatch = "" + airbyteVersion.getMajorVersion()
        + "."
        + airbyteVersion.getMinorVersion()
        + ".0-"
        + airbyteVersion.serialize().replace("\n", "").strip().split("-")[1];
    return new AirbyteVersion(versionWithoutPatch);
  }

  public static AirbyteVersion versionWithoutPatch(final String airbyteVersion) {
    return versionWithoutPatch(new AirbyteVersion(airbyteVersion));
  }

}
