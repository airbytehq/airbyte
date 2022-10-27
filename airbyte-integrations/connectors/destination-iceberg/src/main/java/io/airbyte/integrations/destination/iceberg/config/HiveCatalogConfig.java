package io.airbyte.integrations.destination.iceberg.config;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.CATALOG_NAME;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HIVE_THRIFT_URI_CONFIG_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.HashMap;
import java.util.Map;

/**
 * @author Leibniz on 2022/10/26.
 */
public class HiveCatalogConfig implements IcebergCatalogConfig {

    private final String thriftUri;

    public HiveCatalogConfig(JsonNode catalogConfig) {
        this.thriftUri = catalogConfig.get(HIVE_THRIFT_URI_CONFIG_KEY).asText();
    }

    public HiveCatalogConfig(String thriftUri) {
        this.thriftUri = thriftUri;
    }


    @Override
    public void check(S3Config destinationConfig) {
        if (!thriftUri.startsWith("thrift://")) {
            throw new IllegalArgumentException(HIVE_THRIFT_URI_CONFIG_KEY + " must start with 'thrift://'");
        }
        //TODO check hive metastore thrift uri is available
    }

    @Override
    public Map<String, String> sparkConfigMap(S3Config s3Config) {
        String s3EndpointSchema = s3Config.isSslEnabled() ? "https" : "http";
        String warehouse = "s3a://%s/%s".formatted(s3Config.getBucketName(), s3Config.getBucketPath());
        Map<String, String> configMap = new HashMap<>();
        configMap.put("spark.network.timeout", "300000");
        configMap.put("spark.sql.catalog." + CATALOG_NAME, "org.apache.iceberg.spark.SparkCatalog");
        configMap.put("spark.sql.catalog." + CATALOG_NAME + ".type", "hive");
        configMap.put("spark.sql.catalog." + CATALOG_NAME + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO");
        configMap.put("spark.sql.catalog." + CATALOG_NAME + ".s3.endpoint",
            s3EndpointSchema + "://" + s3Config.getEndpoint());
        configMap.put("spark.sql.catalog." + CATALOG_NAME + ".uri", this.thriftUri);
        configMap.put("spark.sql.catalog." + CATALOG_NAME + ".warehouse", warehouse);
        configMap.put("spark.sql.defaultCatalog", CATALOG_NAME);
        configMap.put("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions");
        //TODO
        configMap.put("spark.driver.extraClassPath", "");
        configMap.put("spark.hadoop.fs.s3a.access.key", s3Config.getAccessKeyId());
        configMap.put("spark.hadoop.fs.s3a.secret.key", s3Config.getSecretKey());
        configMap.put("spark.hadoop.fs.s3a.path.style.access", String.valueOf(s3Config.isPathStyleAccess()));
        configMap.put("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem");
        configMap.put("spark.hadoop.fs.s3a.endpoint", s3Config.getEndpoint());
        configMap.put("spark.hadoop.fs.s3a.connection.ssl.enabled", String.valueOf(s3Config.isSslEnabled()));
        configMap.put("spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider");
        configMap.put("spark.driver.extraJavaOptions", "-Dpackaging.type=jar -Djava.io.tmpdir=/tmp");
        return configMap;
    }
}
