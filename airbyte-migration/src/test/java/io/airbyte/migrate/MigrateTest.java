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

package io.airbyte.migrate;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.ImmutableList;
import io.airbyte.commons.version.AirbyteVersion;
import java.util.List;
import org.junit.jupiter.api.Test;

public class MigrateTest {

  @Test
  void testGetPreviousMigration() {
    final List<AirbyteVersion> versions = ImmutableList.of(
        new AirbyteVersion("0.14.0"),
        new AirbyteVersion("0.14.1"),
        new AirbyteVersion("0.14.4"),
        new AirbyteVersion("0.15.0"));
    assertEquals(0, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.0")));
    assertEquals(1, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.1")));
    assertEquals(1, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.3")));
    assertEquals(2, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.4")));
    assertEquals(2, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.5")));
    assertEquals(3, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.15.0")));
    assertEquals(-1, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.16.0")));
  }

}
