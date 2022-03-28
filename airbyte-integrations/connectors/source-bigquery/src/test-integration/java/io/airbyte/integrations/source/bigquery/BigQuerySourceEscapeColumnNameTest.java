package io.airbyte.integrations.source.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.bigquery.BigQueryDatabase;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.List;

import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_CREDS;
import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_DATASET_ID;
import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_PROJECT_ID;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class BigQuerySourceEscapeColumnNameTest {
    private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
    private static final String STREAM_NAME = "id_and_interval";

    private BigQueryDatabase database;
    private Dataset dataset;
    private JsonNode config;


    @BeforeEach
    void setUp() throws IOException, SQLException {
        if (!Files.exists(CREDENTIALS_PATH)) {
            throw new IllegalStateException(
                    "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
                            + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
        }

        final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);

        final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);
        final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
        final String datasetLocation = "US";

        final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

        config = Jsons.jsonNode(ImmutableMap.builder()
                .put(CONFIG_PROJECT_ID, projectId)
                .put(CONFIG_CREDS, credentialsJsonString)
                .put(CONFIG_DATASET_ID, datasetId)
                .build());

        database = new BigQueryDatabase(config.get(CONFIG_PROJECT_ID).asText(), credentialsJsonString);

        final DatasetInfo datasetInfo =
                DatasetInfo.newBuilder(config.get(CONFIG_DATASET_ID).asText()).setLocation(datasetLocation).build();
        dataset = database.getBigQuery().create(datasetInfo);

        // create column name interval which should be escaped
        database.execute("CREATE TABLE " + datasetId + ".id_and_interval(id INT64, `interval` STRING);");
        database.execute("INSERT INTO " + datasetId + ".id_and_interval (id, `interval`) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    }

    @AfterEach
    void tearDown() {
        database.cleanDataSet(dataset.getDatasetId().getDataset());
    }

    @Test
    public void testReadSuccess() throws Exception {
        final List<AirbyteMessage> actualMessages = MoreIterators.toList(new BigQuerySource().read(config, getConfiguredCatalog(), null));

        actualMessages.get(0).getRecord().getData().get("interval");
        assertNotNull(actualMessages);
        assertEquals(3, actualMessages.size());

        assertNotNull(actualMessages.get(0).getRecord().getData().get("interval"));
        assertNotNull(actualMessages.get(1).getRecord().getData().get("interval"));
        assertNotNull(actualMessages.get(2).getRecord().getData().get("interval"));

    }

    private ConfiguredAirbyteCatalog getConfiguredCatalog() {
        return CatalogHelpers.createConfiguredAirbyteCatalog(
                STREAM_NAME,
                config.get(CONFIG_DATASET_ID).asText(),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("interval", JsonSchemaType.STRING));
    }
}
