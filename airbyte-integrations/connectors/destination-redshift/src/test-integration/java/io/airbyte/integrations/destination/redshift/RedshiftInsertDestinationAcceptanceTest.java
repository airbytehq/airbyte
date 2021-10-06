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

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;

/**
 * Integration test testing the {@link RedshiftInsertDestination}. As the Redshift test credentials
 * contain S3 credentials by default, we remove these credentials.
 */
public class RedshiftInsertDestinationAcceptanceTest extends RedshiftCopyDestinationAcceptanceTest {

  public JsonNode getStaticConfig() {
    return purge(Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json"))));
  }

  public static JsonNode purge(JsonNode config) {
    var original = (ObjectNode) Jsons.clone(config);
    original.remove("s3_bucket_name");
    original.remove("s3_bucket_region");
    original.remove("access_key_id");
    original.remove("secret_access_key");
    return original;
  }

}
