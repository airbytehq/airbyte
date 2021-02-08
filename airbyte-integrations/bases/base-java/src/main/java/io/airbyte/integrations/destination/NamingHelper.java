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

package io.airbyte.integrations.destination;

import java.time.Instant;
import org.apache.commons.lang3.RandomStringUtils;

public class NamingHelper {

  /**
   * Returns the name of a schema for storing raw data associated with a schema name. Make sure to
   * apply the proper naming convention on the final table name for the database
   */
  public static String getTmpSchemaName(NamingConventionTransformer transformer, String schemaName) {
    if (schemaName != null)
      return transformer.getIdentifier("_airbyte_" + schemaName);
    else
      return transformer.getIdentifier("_airbyte");
  }

  /**
   * Returns the name of the table for storing tmp data associated with a stream name. Name is
   * randomly generated.
   */
  public static String getTmpTableName(NamingConventionTransformer transformer, String streamName) {
    return transformer
        .getIdentifier(String.format("_tmp_%s%s_%s", RandomStringUtils.randomAlphanumeric(4), Instant.now().toEpochMilli(), streamName));
  }

}
