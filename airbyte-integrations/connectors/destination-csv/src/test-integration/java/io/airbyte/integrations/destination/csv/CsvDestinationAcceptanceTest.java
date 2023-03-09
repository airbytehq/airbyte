/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.csv;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import io.airbyte.integrations.standardtest.destination.argproviders.DataArgumentsProvider;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;

import java.io.FileReader;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

import io.airbyte.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsSource;

public class CsvDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Path RELATIVE_PATH = Path.of("integration_test/test");
  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/destination-csv:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.of("destination_path", Path.of("/local").resolve(RELATIVE_PATH).toString()));
  }

    protected JsonNode getConfigWithDelimiter(String delimiter) {
    config = Jsons.jsonNode(ImmutableMap.of("destination_path", Path.of("/local").resolve(RELATIVE_PATH).toString(), "delimiter", delimiter));
    return config;
  }

  // todo (cgardens) - it would be great if we could find a configuration here that failed. the
  // commented out one fails in mac but not on the linux box that the github action runs in. instead
  // we override the test here so it never runs.
  @Override
  protected JsonNode getFailCheckConfig() {
    // set the directory to which the integration will try to write to to read only.
    // localRoot.toFile().setReadOnly();

    // return Jsons.jsonNode(ImmutableMap.of("destination_path",
    // Path.of("/local").resolve(RELATIVE_PATH).toString()));
    return null;
  }

  // override test that this integration cannot pass.
  @Override
  public void testCheckConnectionInvalidCredentials() {}


  @ParameterizedTest
  @ArgumentsSource(CSVDataArgumentsProvider.class)
  public void testSyncWithDelimiter(final String messagesFilename, final String catalogFilename, String delimiter)
      throws Exception {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename),
        AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(
        catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class))
        .collect(Collectors.toList());

    final JsonNode config = getConfigWithDelimiter(delimiter);
    final String defaultSchema = getDefaultSchema(config);
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);
    retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final List<Path> allOutputs = Files.list(testEnv.getLocalRoot().resolve(RELATIVE_PATH)).collect(Collectors.toList());

    final Optional<Path> streamOutput =
        allOutputs.stream()
            .filter(path -> path.getFileName().toString().endsWith(new StandardNameTransformer().getRawTableName(streamName) + ".csv"))
            .findFirst();

    assertTrue(streamOutput.isPresent(), "could not find output file for stream: " + streamName);

    final FileReader in = new FileReader(streamOutput.get().toFile(), Charset.defaultCharset());
    final Iterable<CSVRecord> records = CSVFormat.DEFAULT
        .withHeader(JavaBaseConstants.COLUMN_NAME_DATA)
        .withFirstRecordAsHeader()
        .parse(in);

    return StreamSupport.stream(records.spliterator(), false)
        .map(record -> Jsons.deserialize(record.toMap().get(JavaBaseConstants.COLUMN_NAME_DATA)))
        .collect(Collectors.toList());
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    // no op
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    // no op
  }

  public static class CSVDataArgumentsProvider extends DataArgumentsProvider {

    public CSVDataArgumentsProvider(){};
    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      ProtocolVersion protocolVersion = ArgumentProviderUtil.getProtocolVersion(context);
      return Stream.of(
              Arguments.of(EXCHANGE_RATE_CONFIG.getMessageFileVersion(protocolVersion), EXCHANGE_RATE_CONFIG.getCatalogFileVersion(protocolVersion), "\\u002c"),
              Arguments.of(EXCHANGE_RATE_CONFIG.getMessageFileVersion(protocolVersion), EXCHANGE_RATE_CONFIG.getCatalogFileVersion(protocolVersion), "\\u003b"),
              Arguments.of(EXCHANGE_RATE_CONFIG.getMessageFileVersion(protocolVersion), EXCHANGE_RATE_CONFIG.getCatalogFileVersion(protocolVersion), "\\u007c"),
              Arguments.of(EXCHANGE_RATE_CONFIG.getMessageFileVersion(protocolVersion), EXCHANGE_RATE_CONFIG.getCatalogFileVersion(protocolVersion), "\\u0009"),
              Arguments.of(EXCHANGE_RATE_CONFIG.getMessageFileVersion(protocolVersion), EXCHANGE_RATE_CONFIG.getCatalogFileVersion(protocolVersion), "\\u0020")
      );
    }
  }

}
