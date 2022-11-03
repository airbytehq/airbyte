package io.airbyte.integrations.destination.iceberg;

import static io.airbyte.integrations.destination.iceberg.MinioContainer.DEFAULT_ACCESS_KEY;
import static io.airbyte.integrations.destination.iceberg.MinioContainer.DEFAULT_SECRET_KEY;
import static org.sparkproject.jetty.util.StringUtil.isNotBlank;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.Bucket;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.iceberg.MinioContainer.CredentialsProvider;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory;
import io.airbyte.integrations.destination.iceberg.config.storage.S3Config;
import java.io.IOException;
import java.time.OffsetDateTime;
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
import org.testcontainers.containers.GenericContainer;

/**
 * @author Leibniz on 2022/11/3.
 */
public class IcebergIntegrationTestUtil {

    private static final Logger LOGGER = LoggerFactory.getLogger(IcebergIntegrationTestUtil.class);


    public static final String WAREHOUSE_BUCKET_NAME = "warehouse";
    private static final NamingConventionTransformer namingResolver = new StandardNameTransformer();
    private static final IcebergCatalogConfigFactory icebergCatalogConfigFactory = new IcebergCatalogConfigFactory();

    static MinioContainer createAndStartMinioContainer() {
        MinioContainer container = new MinioContainer("minio/minio:RELEASE.2022-10-29T06-21-33Z.fips",
            new CredentialsProvider(DEFAULT_ACCESS_KEY, DEFAULT_SECRET_KEY));
        container.start();
        LOGGER.info("==> Started Minio docker container...");
        return container;
    }

    static void stopAndCloseContainer(GenericContainer<?> container, String name) {
        container.stop();
        container.close();
        LOGGER.info("<== Closed {} docker container...", name);
    }

    static void createS3WarehouseBucket(JsonNode config) {
        IcebergCatalogConfig catalogConfig = icebergCatalogConfigFactory.fromJsonNodeConfig(config);
        AmazonS3 client = ((S3Config) catalogConfig.getStorageConfig()).getS3Client();
        Bucket bucket = client.createBucket(WAREHOUSE_BUCKET_NAME);
        LOGGER.info("Created s3 bucket: {}", bucket.getName());
        List<Bucket> buckets = client.listBuckets();
        LOGGER.info("All s3 buckets: {}", buckets);
    }

    static List<JsonNode> retrieveRecords(JsonNode config, String namespace, String streamName) throws IOException {
        IcebergCatalogConfig catalogConfig = icebergCatalogConfigFactory.fromJsonNodeConfig(config);
        Catalog catalog = catalogConfig.genCatalog();
        String dbName = namingResolver.getNamespace(
            isNotBlank(namespace) ? namespace : catalogConfig.defaultOutputDatabase()).toLowerCase();
        String tableName = namingResolver.getIdentifier("airbyte_raw_" + streamName).toLowerCase();
        LOGGER.info("Select data from:{}", tableName);
        Table table = catalog.loadTable(TableIdentifier.of(dbName, tableName));
        try (CloseableIterable<Record> records = IcebergGenerics.read(table).build()) {
            return Lists.newArrayList(records)
                .stream()
                .sorted((r1, r2) -> Comparator.<OffsetDateTime>naturalOrder()
                    .compare((OffsetDateTime) r1.getField(JavaBaseConstants.COLUMN_NAME_EMITTED_AT),
                        (OffsetDateTime) r2.getField(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)))
                .map(r -> Jsons.deserialize((String) r.getField(JavaBaseConstants.COLUMN_NAME_DATA)))
                .collect(Collectors.toList());
        }
    }
}
