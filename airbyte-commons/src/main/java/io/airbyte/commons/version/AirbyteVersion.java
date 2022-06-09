/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

import com.google.common.base.Preconditions;
import java.util.Objects;

/**
 * The AirbyteVersion identifies the version of the database used internally by Airbyte services.
 */
public class AirbyteVersion {

  public static final String DEV_VERSION_PREFIX = "dev";
  public static final String AIRBYTE_VERSION_KEY_NAME = "airbyte_version";

  private final String version;
  private final String major;
  private final String minor;
  private final String patch;

  public AirbyteVersion(final String version) {
    Preconditions.checkNotNull(version);
    this.version = version;
    final String[] parsedVersion = version.replace("\n", "").strip().split("-")[0].split("\\.");

    if (isDev()) {
      this.major = null;
      this.minor = null;
      this.patch = null;
    } else {
      Preconditions.checkArgument(parsedVersion.length >= 3, "Invalid version string: " + version);
      this.major = parsedVersion[0];
      this.minor = parsedVersion[1];
      this.patch = parsedVersion[2];
    }
  }

  public AirbyteVersion(final String major, final String minor, final String patch) {
    this.version = String.format("%s.%s.%s", major, minor, patch);
    this.major = major;
    this.minor = minor;
    this.patch = patch;
  }

  public String serialize() {
    return version;
  }

  public String getMajorVersion() {
    return major;
  }

  public String getMinorVersion() {
    return minor;
  }

  public String getPatchVersion() {
    return patch;
  }

  /**
   * Compares two Airbyte Version to check if they are equivalent.
   *
   * Only the major and minor part of the Version is taken into account.
   */
  public int compatibleVersionCompareTo(final AirbyteVersion another) {
    if (isDev() || another.isDev())
      return 0;
    final int majorDiff = compareVersion(major, another.major);
    if (majorDiff != 0) {
      return majorDiff;
    }
    return compareVersion(minor, another.minor);
  }

  /**
   * @return true if this is greater than other. otherwise false.
   */
  public boolean greaterThan(final AirbyteVersion other) {
    return patchVersionCompareTo(other) > 0;
  }

  /**
   * @return true if this is greater than or equal toother. otherwise false.
   */
  public boolean greaterThanOrEqualTo(final AirbyteVersion other) {
    return patchVersionCompareTo(other) >= 0;
  }

  /**
   * @return true if this is less than other. otherwise false.
   */
  public boolean lessThan(final AirbyteVersion other) {
    return patchVersionCompareTo(other) < 0;
  }

  /**
   * Compares two Airbyte Version to check if they are equivalent (including patch version).
   */
  public int patchVersionCompareTo(final AirbyteVersion another) {
    if (isDev() || another.isDev()) {
      return 0;
    }
    final int majorDiff = compareVersion(major, another.major);
    if (majorDiff != 0) {
      return majorDiff;
    }
    final int minorDiff = compareVersion(minor, another.minor);
    if (minorDiff != 0) {
      return minorDiff;
    }
    return compareVersion(patch, another.patch);
  }

  /**
   * Compares two Airbyte Version to check if only the patch version was updated.
   */
  public boolean checkOnlyPatchVersionIsUpdatedComparedTo(final AirbyteVersion another) {
    if (isDev() || another.isDev()) {
      return false;
    }
    final int majorDiff = compareVersion(major, another.major);
    if (majorDiff > 0) {
      return false;
    }
    final int minorDiff = compareVersion(minor, another.minor);
    if (minorDiff > 0) {
      return false;
    }
    return compareVersion(patch, another.patch) > 0;
  }

  public boolean isDev() {
    return version.startsWith(DEV_VERSION_PREFIX);
  }

  /**
   * Version string needs to be converted to integer for comparison, because string comparison does
   * not handle version string with different digits correctly. For example:
   * {@code "11".compare("3") < 0}, while {@code Integer.compare(11, 3) > 0}.
   */
  private static int compareVersion(final String v1, final String v2) {
    return Integer.compare(Integer.parseInt(v1), Integer.parseInt(v2));
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

  public static boolean isCompatible(final AirbyteVersion v1, final AirbyteVersion v2) {
    return v1.compatibleVersionCompareTo(v2) == 0;
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

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final AirbyteVersion that = (AirbyteVersion) o;
    return Objects.equals(version, that.version) && Objects.equals(major, that.major) && Objects.equals(minor, that.minor)
        && Objects.equals(patch, that.patch);
  }

  @Override
  public int hashCode() {
    return Objects.hash(version, major, minor, patch);
  }

}
