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

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class SnowflakeDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("When given S3 credentials should use COPY")
  public void useS3CopyStrategyTest() {
    var stubLoadingMethod = mapper.createObjectNode();
    stubLoadingMethod.put("s3_bucket_name", "fake-bucket");
    stubLoadingMethod.put("access_key_id", "test");
    stubLoadingMethod.put("secret_access_key", "test key");

    var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);

    assertTrue(SnowflakeDestination.isS3Copy(stubConfig));
  }

  @Test
  @DisplayName("When given GCS credentials should use COPY")
  public void useGcsCopyStrategyTest() {
    var stubLoadingMethod = mapper.createObjectNode();
    stubLoadingMethod.put("project_id", "my-project");
    stubLoadingMethod.put("bucket_name", "my-bucket");
    stubLoadingMethod.put("credentials_json", "hunter2");

    var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);

    assertTrue(SnowflakeDestination.isGcsCopy(stubConfig));
  }

  @Test
  @DisplayName("When not given S3 credentials should use INSERT")
  public void useInsertStrategyTest() {
    var stubLoadingMethod = mapper.createObjectNode();
    var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);
    assertFalse(SnowflakeDestination.isS3Copy(stubConfig));
  }

}
