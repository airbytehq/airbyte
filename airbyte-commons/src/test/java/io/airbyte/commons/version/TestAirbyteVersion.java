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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

public class TestAirbyteVersion {

  @Test
  public void testParseVersion() {
    final AirbyteVersion version = new AirbyteVersion("6.7.8");
    assertEquals("6", version.getMajorVersion());
    assertEquals("7", version.getMinorVersion());
    assertEquals("8", version.getPatchVersion());
  }

  @Test
  public void testParseVersionWithLabel() {
    final AirbyteVersion version = new AirbyteVersion("6.7.8-omega");
    assertEquals("6", version.getMajorVersion());
    assertEquals("7", version.getMinorVersion());
    assertEquals("8", version.getPatchVersion());
  }

  @Test
  public void testCompatibleVersionCompareTo() {
    assertEquals(0, new AirbyteVersion("6.7.8-omega").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-gamma")));
    assertEquals(0, new AirbyteVersion("6.7.8-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.9-alpha")));
    assertTrue(0 < new AirbyteVersion("6.8.0-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 < new AirbyteVersion("11.8.0-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 < new AirbyteVersion("6.11.0-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 > new AirbyteVersion("0.8.0-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertEquals(0, new AirbyteVersion("1.2.3-prod").compatibleVersionCompareTo(new AirbyteVersion("dev")));
    assertEquals(0, new AirbyteVersion("dev").compatibleVersionCompareTo(new AirbyteVersion("1.2.3-prod")));
  }

  @Test
  public void testPatchVersionCompareTo() {
    assertEquals(0, new AirbyteVersion("6.7.8-omega").patchVersionCompareTo(new AirbyteVersion("6.7.8-gamma")));
    assertTrue(0 > new AirbyteVersion("6.7.8-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.9-alpha")));
    assertTrue(0 > new AirbyteVersion("6.7.8-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.11-alpha")));
    assertTrue(0 < new AirbyteVersion("6.8.0-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 < new AirbyteVersion("6.11.0-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 > new AirbyteVersion("3.8.0-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 > new AirbyteVersion("3.8.0-alpha").patchVersionCompareTo(new AirbyteVersion("11.7.8-alpha")));
    assertEquals(0, new AirbyteVersion("1.2.3-prod").patchVersionCompareTo(new AirbyteVersion("dev")));
    assertEquals(0, new AirbyteVersion("dev").patchVersionCompareTo(new AirbyteVersion("1.2.3-prod")));
  }

  @Test
  public void testInvalidVersions() {
    assertThrows(NullPointerException.class, () -> new AirbyteVersion(null));
    assertThrows(IllegalArgumentException.class, () -> new AirbyteVersion("0.6"));
  }

  @Test
  public void testCheckVersion() {
    AirbyteVersion.assertIsCompatible("3.2.1", "3.2.1");
    assertThrows(IllegalStateException.class, () -> AirbyteVersion.assertIsCompatible("1.2.3", "3.2.1"));
  }

}
