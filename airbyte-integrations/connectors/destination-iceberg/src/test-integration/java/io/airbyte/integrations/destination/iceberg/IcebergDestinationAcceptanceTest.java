/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import static org.sparkproject.jetty.util.StringUtil.isNotBlank;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.iceberg.config.S3Config;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.nio.file.Path;
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.iceberg.Table;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.catalog.TableIdentifier;
import org.apache.iceberg.data.IcebergGenerics;
import org.apache.iceberg.data.Record;
import org.apache.iceberg.io.CloseableIterable;
import org.glassfish.jersey.internal.guava.Lists;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class IcebergDestinationAcceptanceTest extends DestinationAcceptanceTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(IcebergDestinationAcceptanceTest.class);

    private static final String SECRET_FILE_PATH = "secrets/iceberg.json";
    private final NamingConventionTransformer namingResolver = new StandardNameTransformer();

    @Override
    protected String getImageName() {
        return "airbyte/destination-iceberg:dev";
    }

    @Override
    protected JsonNode getConfig() throws IOException {
        return Jsons.deserialize(IOs.readFile(Path.of(SECRET_FILE_PATH)));
    }

    @Override
    protected JsonNode getFailCheckConfig() {
        final JsonNode failCheckJson = Jsons.jsonNode(Collections.emptyMap());
        // invalid credential
        ((ObjectNode) failCheckJson).put("access_key_id", "fake-key");
        ((ObjectNode) failCheckJson).put("secret_access_key", "fake-secret");
        return failCheckJson;
    }

    @Override
    protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
        String streamName,
        String namespace,
        JsonNode streamSchema)
        throws IOException {
        // Records returned from this method will be compared against records provided to the connector
        // to verify they were written correctly
        JsonNode config = getConfig();
        final S3Config s3Config = new S3Config.S3ConfigFactory().parseS3Config(config);
        Catalog catalog = s3Config.getCatalogConfig().genCatalog(s3Config);

        String dbName = namingResolver.getNamespace(
            isNotBlank(namespace) ? namespace :
                s3Config.getCatalogConfig().getDefaultDatabase()
        ).toLowerCase();
        String tableName = namingResolver.getIdentifier("airbyte_raw_" + streamName).toLowerCase();
        LOGGER.info("Select data from:{}", tableName);
        Table table = catalog.loadTable(TableIdentifier.of(dbName, tableName));
        try (CloseableIterable<Record> records = IcebergGenerics.read(table).build()) {
            return Lists.newArrayList(records)
                .stream()
                .sorted((r1, r2) -> Comparator.<OffsetDateTime>naturalOrder().compare(
                    (OffsetDateTime) r1.getField(JavaBaseConstants.COLUMN_NAME_EMITTED_AT),
                    (OffsetDateTime) r2.getField(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
                ))
                .map(r -> Jsons.deserialize((String) r.getField(JavaBaseConstants.COLUMN_NAME_DATA)))
                .collect(Collectors.toList());
        }
    }

    @Override
    protected void setup(TestDestinationEnv testEnv) throws IOException {
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {
    }

}
