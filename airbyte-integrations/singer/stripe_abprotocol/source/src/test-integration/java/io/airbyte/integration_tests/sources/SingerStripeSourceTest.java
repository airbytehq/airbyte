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

package io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.stripe.exception.StripeException;
import com.stripe.model.Customer;
import com.stripe.net.RequestOptions;
import com.stripe.param.CustomerCreateParams;
import com.stripe.param.CustomerListParams;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SingerStripeSourceTest {

  private static final Path TESTS_PATH = Path.of("/tmp/airbyte_integration_tests");
  private static final String IMAGE_NAME = "airbyte/source-stripe-abprotocol-singer:dev";

  private static final String CATALOG = "catalog.json";
  private static final String CONFIG = "config.json";
  private static final String CONFIG_PATH = "secrets/config.json";
  private static final String INVALID_CONFIG = "invalid_config.json";

  protected Path jobRoot;
  protected Path workspaceRoot;
  protected IntegrationLauncher launcher;
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

    launcher = new AirbyteIntegrationLauncher(
        IMAGE_NAME,
        new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "", "host"));
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
  public void testGetSpec() throws WorkerException, IOException, InterruptedException {
    Process process = launcher.spec(jobRoot).start();
    process.waitFor();

    InputStream expectedSpecInputStream = Objects.requireNonNull(getClass().getClassLoader().getResourceAsStream("spec.json"));

    assertEquals(
        new AirbyteMessage().withType(Type.SPEC)
            .withSpec(Jsons.deserialize(new String(expectedSpecInputStream.readAllBytes()), ConnectorSpecification.class)),
        Jsons.deserialize(new String(process.getInputStream().readAllBytes()), AirbyteMessage.class));
  }

  @Test
  public void testSuccessfulCheck() throws IOException, InterruptedException, WorkerException {
    Process process = launcher.check(jobRoot, CONFIG).start();
    process.waitFor();

    assertEquals(0, process.exitValue());

    final Optional<String> statusMessageString =
        new BufferedReader(new InputStreamReader(process.getInputStream())).lines().filter(s -> s.contains("CONNECTION_STATUS")).findFirst();

    assertTrue(statusMessageString.isPresent());
    assertEquals(
        new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED)),
        Jsons.deserialize(statusMessageString.get(), AirbyteMessage.class));
  }

  @Test
  public void testInvalidCredentialsCheck() throws IOException, InterruptedException, WorkerException {
    Process process = launcher.check(jobRoot, INVALID_CONFIG).start();
    process.waitFor();

    assertEquals(0, process.exitValue());

    final Optional<String> statusMessageString =
        new BufferedReader(new InputStreamReader(process.getInputStream())).lines().filter(s -> s.contains("CONNECTION_STATUS")).findFirst();
    assertTrue(statusMessageString.isPresent());

    AirbyteMessage response = Jsons.deserialize(statusMessageString.get(), AirbyteMessage.class);
    assertEquals(Type.CONNECTION_STATUS, response.getType());
    assertEquals(Status.FAILED, response.getConnectionStatus().getStatus());
    assertTrue(response.getConnectionStatus().getMessage().length() > 0);
  }

  @Test
  public void testSuccessfulDiscover() throws IOException, InterruptedException, WorkerException {
    Process process = createDiscoveryProcess(CONFIG);
    process.waitFor();

    assertEquals(0, process.exitValue());

    final String catalog = IOs.readFile(jobRoot, catalogPath.toString());

    assertTrue(catalog.length() > 20000);
    assertTrue(catalog.contains("customer"));
    assertTrue(catalog.contains("address_zip_check"));
  }

  @Test
  public void testSync() throws IOException, InterruptedException, WorkerException {
    String catalog = MoreResources.readResource(CATALOG);
    IOs.writeFile(catalogPath.getParent(), catalogPath.getFileName().toString(), catalog);

    // run syn process
    Path syncOutputPath = jobRoot.resolve("sync_output.txt");
    Process process = createSyncProcess(syncOutputPath);
    process.waitFor(1, TimeUnit.MINUTES);

    assertEquals(0, process.exitValue());

    final Set<JsonNode> actualSyncOutput = IOs.readFile(jobRoot, syncOutputPath.toString()).lines()
        .map(Jsons::deserialize)
        .map(SingerStripeSourceTest::normalize)
        .collect(Collectors.toSet());

    MoreResources.readResource("sync_output_subset.txt").lines()
        .map(Jsons::deserialize)
        .map(SingerStripeSourceTest::normalize)
        .forEach(record -> assertTrue(actualSyncOutput.contains(record), "Actual output: " + actualSyncOutput));
  }

  private static JsonNode normalize(JsonNode node) {
    ObjectNode normalized = node.deepCopy();

    if (normalized.get("type").textValue().equals("RECORD")) {
      ObjectNode data = (ObjectNode) normalized.get("record").get("data");
      data.put("id", "id");
      data.put("created", "created");
      data.put("invoice_prefix", "invoice_prefix");
      data.put("updated", "updated");

      ObjectNode record = ((ObjectNode) normalized.get("record"));
      record.replace("data", data);
      record.put("emitted_at", 0);
    }

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

    Files.writeString(Path.of(jobRoot.toString(), INVALID_CONFIG), Jsons.serialize(fullConfig));
  }

  private Process createDiscoveryProcess(String configFileName) throws IOException, WorkerException {
    return launcher.discover(jobRoot, configFileName)
        .redirectOutput(catalogPath.toFile())
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private Process createSyncProcess(Path syncOutputPath) throws IOException, WorkerException {
    return launcher.read(jobRoot, CONFIG, CATALOG)
        .redirectOutput(syncOutputPath.toFile())
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

}
