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

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.TestSource;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;

public class RedshiftIntegrationTests extends TestSource {

  // From the AWS tutorial, data was pre-loaded in redshift:
  // https://docs.aws.amazon.com/redshift/latest/dg/tutorial-loading-data.html
  // This test case expects a tables public.customer(c_custkey, c_name, c_nation) to be loaded on a
  // active redshift cluster
  // that is useable from outside of vpc
  private static final String STREAM_NAME = "public.customer";
  private JsonNode config;

  private static JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    config = getStaticConfig();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {

  }

  @Override
  protected String getImageName() {
    return "airbyte/source-redshift:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected AirbyteCatalog getCatalog() {
    return CatalogHelpers.createAirbyteCatalog(
        STREAM_NAME,
        Field.of("c_custkey", Field.JsonSchemaPrimitive.NUMBER),
        Field.of("c_name", Field.JsonSchemaPrimitive.STRING),
        Field.of("c_nation", Field.JsonSchemaPrimitive.STRING));
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

}
