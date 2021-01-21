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

package io.airbyte.db;

/**
 * The AirbyteVersion identifies the version of the database used internally by Airbyte services.
 */
public class AirbyteVersion implements Comparable<AirbyteVersion> {

  public static final String AIRBYTE_VERSION_KEY_NAME = "airbyte_version";

  private final String major;
  private final String minor;
  private final String patch;

  public AirbyteVersion(final String version) {
    final String[] parsedVersion = version.replace("\n", "").strip().split("-")[0].split("\\.");
    if (parsedVersion.length >= 3) {
      major = parsedVersion[0];
      minor = parsedVersion[1];
      patch = parsedVersion[2];
    } else {
      major = version;
      minor = "";
      patch = "";
    }
  }

  /**
   * Compares two Airbyte Version to check if they are equivalent.
   *
   * Only the major and minor part of the Version is taken into account.
   */
  @Override
  public int compareTo(final AirbyteVersion another) {
    final int majorDiff = major.compareTo(another.major);
    if (majorDiff != 0) {
      return majorDiff;
    }
    return minor.compareTo(another.minor);
  }

  public static void check(final String version1, final String version2) throws IllegalStateException {
    final String cleanVersion1 = version1.replace("\n", "").strip();
    final String cleanVersion2 = version2.replace("\n", "").strip();
    if (isInvalid(version1, version2)) {
      throw new IllegalStateException(String.format(
          "Version mismatch between %s and %s.\n" +
              "Please Upgrade or Reset your Airbyte Database, see more at https://docs.airbyte.io/tutorials/tutorials/upgrading-airbyte",
          cleanVersion1, cleanVersion2));
    }
  }

  public static boolean isInvalid(final String v1, final String v2) {
    final AirbyteVersion version1 = new AirbyteVersion(v1);
    final AirbyteVersion version2 = new AirbyteVersion(v2);
    return version1.compareTo(version2) != 0;
  }

}
