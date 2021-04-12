/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.commons.version;

import com.google.common.base.Preconditions;

/**
 * The AirbyteVersion identifies the version of the database used internally by Airbyte services.
 */
public class AirbyteVersion {

  private static final String DEV_VERSION = "dev";
  public static final String AIRBYTE_VERSION_KEY_NAME = "airbyte_version";

  private final String version;
  private final String major;
  private final String minor;
  private final String patch;

  public AirbyteVersion(final String version) {
    Preconditions.checkNotNull(version);
    this.version = version;
    final String[] parsedVersion = version.replace("\n", "").strip().split("-")[0].split("\\.");

    if (version.equals(DEV_VERSION)) {
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

  public String getVersion() {
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
    if (version.equals(DEV_VERSION) || another.version.equals(DEV_VERSION))
      return 0;
    final int majorDiff = major.compareTo(another.major);
    if (majorDiff != 0) {
      return majorDiff;
    }
    return minor.compareTo(another.minor);
  }

  /**
   * Compares two Airbyte Version to check if they are equivalent (including patch version).
   */
  public int patchVersionCompareTo(final AirbyteVersion another) {
    if (version.equals(DEV_VERSION) || another.version.equals(DEV_VERSION)) {
      return 0;
    }
    final int majorDiff = major.compareTo(another.major);
    if (majorDiff != 0) {
      return majorDiff;
    }
    final int minorDiff = minor.compareTo(another.minor);
    if (minorDiff != 0) {
      return minorDiff;
    }
    return patch.compareTo(another.patch);
  }

  public static void assertIsCompatible(final String version1, final String version2) throws IllegalStateException {
    final String cleanVersion1 = version1.replace("\n", "").strip();
    final String cleanVersion2 = version2.replace("\n", "").strip();
    if (isCompatible(version1, version2)) {
      throw new IllegalStateException(String.format(
          "Version mismatch between %s and %s.\n" +
              "Please upgrade or reset your Airbyte Database, see more at https://docs.airbyte.io/tutorials/upgrading-airbyte",
          cleanVersion1, cleanVersion2));
    }
  }

  public static boolean isCompatible(final String v1, final String v2) {
    final AirbyteVersion version1 = new AirbyteVersion(v1);
    final AirbyteVersion version2 = new AirbyteVersion(v2);
    return version1.compatibleVersionCompareTo(version2) != 0;
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

}
