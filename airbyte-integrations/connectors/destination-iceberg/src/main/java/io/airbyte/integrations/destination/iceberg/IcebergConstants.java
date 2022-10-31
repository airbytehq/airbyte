package io.airbyte.integrations.destination.iceberg;

/**
 * @author Leibniz on 2022/10/26.
 */
public class IcebergConstants {

    /**
     * Root Config keys
     */
    public static final String ICEBERG_CATALOG_CONFIG_KEY = "catalog_config";
    public static final String ICEBERG_STORAGE_CONFIG_KEY = "storage_config";
    public static final String ICEBERG_FORMAT_CONFIG_KEY = "format_config";

    /**
     * Catalog Config keys
     */
    public static final String ICEBERG_CATALOG_TYPE_CONFIG_KEY = "catalog_type";
    public static final String HIVE_THRIFT_URI_CONFIG_KEY = "hive_thrift_uri";
    public static final String HIVE_DATABASE_CONFIG_KEY = "database";

    /**
     * Storage Config keys
     */
    public static final String ICEBERG_STORAGE_TYPE_CONFIG_KEY = "storage_type";
    public static final String S3_ACCESS_KEY_ID_CONFIG_KEY = "access_key_id";
    public static final String S3_SECRET_KEY_CONFIG_KEY = "secret_access_key";
    public static final String S3_WAREHOUSE_URI_CONFIG_KEY = "s3_warehouse_uri";
    public static final String S3_BUCKET_REGION_CONFIG_KEY = "s3_bucket_region";
    public static final String S3_ENDPOINT_CONFIG_KEY = "s3_endpoint";
    public static final String S3_PATH_STYLE_ACCESS_CONFIG_KEY = "s3_path_style_access";

    /**
     * Format Config keys
     */
    public static final String FORMAT_TYPE_CONFIG_KEY = "format";


    public static final String CATALOG_NAME = "iceberg";
    public static final String DEFAULT_DATABASE = "default";
}
