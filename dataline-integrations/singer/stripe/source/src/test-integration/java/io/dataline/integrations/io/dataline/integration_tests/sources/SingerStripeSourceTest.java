/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.integrations.io.dataline.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Charsets;
import com.stripe.exception.StripeException;
import com.stripe.model.Customer;
import com.stripe.net.RequestOptions;
import com.stripe.param.CustomerCreateParams;
import com.stripe.param.CustomerListParams;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.workers.process.DockerProcessBuilderFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerStripeSourceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerStripeSourceTest.class);

  private static final Path TESTS_PATH = Path.of("/tmp/dataline_integration_tests");
  private static final String IMAGE_NAME = "dataline/integration-singer-stripe-source:dev";

  private static final String CATALOG = "catalog.json";
  private static final String CONFIG = "config.json";
  private static final String CONFIG_PATH = "config/config.json";
  private static final String INVALID_CONFIG = "invalid_config.json";

  protected Path jobRoot;
  protected Path workspaceRoot;
  protected ProcessBuilderFactory pbf;
  protected Path catalogPath;

  @BeforeEach
  public void setUp() throws IOException, StripeException {
    createTestRecordsIfNonExistent();

    Files.createDirectories(TESTS_PATH);
    workspaceRoot = Files.createTempDirectory(TESTS_PATH, "stripe");
    jobRoot = Path.of(workspaceRoot.toString(), "job");
    Files.createDirectories(jobRoot);

    catalogPath = jobRoot.resolve(CATALOG);

    writeConfigFilesToJobRoot();

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "host");
  }

  private static String getEmail(int number) {
    return "customer" + number + "@test.com";
  }

  private void createTestRecordsIfNonExistent() throws IOException, StripeException {
    String credentialsJsonString = new String(Files.readAllBytes(Paths.get(CONFIG_PATH)));
    JsonNode credentials = Jsons.deserialize(credentialsJsonString);
    String stripeApiKey = credentials.get("client_secret").textValue();

    RequestOptions requestOptions = RequestOptions.builder()
        .setApiKey(stripeApiKey)
        .build();

    for (int i = 1; i <= 4; i++) {
      String email = getEmail(i);
      String phone = "" + i + i + i + "-" + i + i + i + "-" + i + i + i + i;
      String description = "Customer " + i;

      List<Customer> customers = Customer.list(CustomerListParams.builder().setEmail(email).build(), requestOptions).getData();

      if (customers.isEmpty()) {
        Customer.create(
            CustomerCreateParams.builder()
                .setEmail(email)
                .setDescription(description)
                .setPhone(phone)
                .build(),
            requestOptions);
      }
    }
  }

  @Test
  public void testInvalidCredentialsDiscover() throws IOException, InterruptedException {
    Process process = createDiscoveryProcess(INVALID_CONFIG);
    process.waitFor();

    assertEquals(2, process.exitValue());
  }

  @Test
  public void testSuccessfulDiscover() throws IOException, InterruptedException {
    Process process = createDiscoveryProcess(CONFIG);
    process.waitFor();

    assertEquals(0, process.exitValue());

    final String catalog = IOs.readFile(jobRoot, catalogPath.toString());

    assertTrue(catalog.lines().count() > 10000);
    assertTrue(catalog.contains("customer"));
    assertTrue(catalog.contains("address_zip_check"));
  }

  @Test
  public void testSync() throws IOException, InterruptedException {
    InputStream catalogStream = getClass().getClassLoader().getResourceAsStream(CATALOG);
    String catalog = IOUtils.toString(catalogStream, Charsets.UTF_8);
    IOs.writeFile(catalogPath.getParent(), catalogPath.getFileName().toString(), catalog);

    // run syn process
    Path syncOutputPath = jobRoot.resolve("sync_output.txt");
    Process process = createSyncProcess(syncOutputPath);
    process.waitFor();

    assertEquals(0, process.exitValue());

    final Set<JsonNode> actualSyncOutput = IOs.readFile(jobRoot, syncOutputPath.toString()).lines()
        .map(Jsons::deserialize)
        .map(SingerStripeSourceTest::normalize)
        .collect(Collectors.toSet());

    InputStream expectedStream = getClass().getClassLoader().getResourceAsStream("sync_output_subset.txt");
    IOUtils.toString(expectedStream, Charsets.UTF_8).lines()
        .map(Jsons::deserialize)
        .map(SingerStripeSourceTest::normalize)
        .forEach(record -> assertTrue(actualSyncOutput.contains(record)));
  }

  private static JsonNode normalize(JsonNode node) {
    ObjectNode normalized = node.deepCopy();

    if (normalized.get("type").textValue().equals("RECORD")) {
      ObjectNode record = (ObjectNode) normalized.get("record");
      record.put("id", "id");
      record.put("created", "created");
      record.put("invoice_prefix", "invoice_prefix");
      record.put("updated", "updated");

      normalized.replace("record", record);
    }

    normalized.put("time_extracted", "time_extracted");

    return normalized;
  }

  private void writeConfigFilesToJobRoot() throws IOException {
    writeValidConfigFile();
    writeInvalidConfigFile();
  }

  private void writeValidConfigFile() throws IOException {
    String credentialsJsonString = new String(Files.readAllBytes(Paths.get(CONFIG_PATH)));
    JsonNode credentials = Jsons.deserialize(credentialsJsonString);

    assertTrue(credentials.get("client_secret").textValue().startsWith("sk_test_"));
    assertTrue(credentials.get("account_id").textValue().startsWith("acct_"));
    assertEquals("2017-01-01T00:00:00Z", credentials.get("start_date").textValue());

    Files.writeString(
        Path.of(jobRoot.toString(), "config.json"), credentialsJsonString);
  }

  private void writeInvalidConfigFile() throws IOException {
    Map<String, Object> fullConfig = new HashMap<>();

    fullConfig.put("client_secret", "sk_test_" + RandomStringUtils.randomAlphanumeric(20));
    fullConfig.put("account_id", "acct_" + RandomStringUtils.randomAlphanumeric(20));
    fullConfig.put("start_date", "2017-01-01T00:00:00Z");

    Files.writeString(
        Path.of(jobRoot.toString(), INVALID_CONFIG), Jsons.serialize(fullConfig));
  }

  private Process createDiscoveryProcess(String configFileName) throws IOException {
    return pbf.create(
        jobRoot,
        IMAGE_NAME,
        "--config",
        configFileName,
        "--discover")
        .redirectOutput(catalogPath.toFile())
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private Process createSyncProcess(Path syncOutputPath) throws IOException {
    return pbf.create(
        jobRoot,
        IMAGE_NAME,
        "--config",
        CONFIG,
        "--catalog",
        CATALOG)
        .redirectOutput(syncOutputPath.toFile())
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

}
