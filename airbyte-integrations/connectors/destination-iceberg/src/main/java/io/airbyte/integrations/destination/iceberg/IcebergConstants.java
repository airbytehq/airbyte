package io.airbyte.integrations.destination.iceberg;

/**
 * @author Leibniz on 2022/10/26.
 */
public class IcebergConstants {

    /**
     * Config keys
     */
    public static final String S3_ACCESS_KEY_ID_CONFIG_KEY = "access_key_id";
    public static final String S3_SECRET_KEY_CONFIG_KEY = "secret_access_key";
    public static final String S3_BUCKET_NAME_CONFIG_KEY = "s3_bucket_name";
    public static final String S3_BUCKET_PATH_CONFIG_KEY = "s3_bucket_path";
    public static final String S3_BUCKET_REGION_CONFIG_KEY = "s3_bucket_region";
    public static final String S3_ENDPOINT_CONFIG_KEY = "s3_endpoint";
    public static final String S3_PATH_STYLE_ACCESS_CONFIG_KEY = "s3_path_style_access";
    public static final String S3_SSL_ENABLED_CONFIG_KEY = "s3_ssl_enabled";

    public static final String ICEBERG_CATALOG_CONFIG_KEY = "iceberg_catalog";
    public static final String ICEBERG_CATALOG_TYPE_CONFIG_KEY = "catalog_type";
    public static final String HIVE_THRIFT_URI_CONFIG_KEY = "hive_thrift_uri";
}
