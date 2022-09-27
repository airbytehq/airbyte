/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iomete;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.constant.S3Constants;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;

public class IometeDestinationConfig {

    static final String DEFAULT_WAREHOUSE_PORT = "443";
    static final String DEFAULT_DATABASE_SCHEMA = "default";
    static final boolean DEFAULT_PURGE_STAGING_DATA = true;
    static final boolean DEFAULT_SSL_CONNECTION = true;

    private final String warehouseHostname;
    private final String warehouseName;
    private final String warehousePort;
    private final boolean isSSL;
    private final String iometeAccountNumber;
    private final String iometeUsername;
    private final String iometePassword;
    private final String databaseSchema;
    private final boolean purgeStagingData;
    private final S3DestinationConfig s3DestinationConfig;

    public IometeDestinationConfig(
            final String warehouseHostname,
            final String warehouseName,
            final String warehousePort,
            final boolean isSSL,
            final String iometeAccountNumber,
            final String iometeUsername,
            final String iometePassword,
            final String databaseSchema,
            final boolean purgeStagingData,
            final S3DestinationConfig s3DestinationConfig) {
        this.warehouseHostname = warehouseHostname;
        this.warehouseName = warehouseName;
        this.warehousePort = warehousePort;
        this.isSSL = isSSL;
        this.iometeAccountNumber = iometeAccountNumber;
        this.iometeUsername = iometeUsername;
        this.iometePassword = iometePassword;
        this.databaseSchema = databaseSchema;
        this.purgeStagingData = purgeStagingData;
        this.s3DestinationConfig = s3DestinationConfig;
    }


    public static IometeDestinationConfig get(final JsonNode config) {
        return new IometeDestinationConfig(
                config.get("warehouse_hostname").asText(),
                config.get("warehouse_name").asText(),
                config.has("warehouse_port") ? config.get("warehouse_port").asText() : DEFAULT_WAREHOUSE_PORT,
                config.has("ssl") ? config.get("ssl").asBoolean() : DEFAULT_SSL_CONNECTION,
                config.get("iomete_account_number").asText(),
                config.get("iomete_username").asText(),
                config.get("iomete_password").asText(),
                config.has("database_schema") ? config.get("database_schema").asText() : DEFAULT_DATABASE_SCHEMA,
                config.has("purge_staging_data") ? config.get("purge_staging_data").asBoolean() : DEFAULT_PURGE_STAGING_DATA,
                getDataSource(config.get("data_source")));
    }

    public static S3DestinationConfig getDataSource(final JsonNode dataSource) {
        final S3DestinationConfig.Builder builder = S3DestinationConfig.create(
            dataSource.get(S3Constants.S_3_BUCKET_NAME).asText(),
            dataSource.get(S3Constants.S_3_BUCKET_PATH).asText(),
            dataSource.get(S3Constants.S_3_BUCKET_REGION).asText())
            .withAccessKeyCredential(
                    dataSource.get(S3Constants.S_3_ACCESS_KEY_ID).asText(),
                    dataSource.get(S3Constants.S_3_SECRET_ACCESS_KEY).asText())
            .withFormatConfig(getDefaultParquetConfig());
        if (dataSource.has(S3Constants.FILE_NAME_PATTERN)) {
            builder.withFileNamePattern(dataSource.get(S3Constants.FILE_NAME_PATTERN).asText());
        }
        return builder.get();
    }

    private static S3ParquetFormatConfig getDefaultParquetConfig() {
        return new S3ParquetFormatConfig(new ObjectMapper().createObjectNode());
    }

    public String getWarehouseHostname() {
        return warehouseHostname;
    }

    public String getWarehouseName() {
        return warehouseName;
    }

    public String getWarehousePort() {
        return warehousePort;
    }

    public boolean isSSL() {
        return isSSL;
    }

    public String getIometeAccountNumber() {
        return iometeAccountNumber;
    }
    public String getIometeUsername() {
        return iometeUsername;
    }

    public String getIometePassword() {
        return iometePassword;
    }

    public String getDatabaseSchema() {
        return databaseSchema;
    }

    public boolean isPurgeStagingData() {
        return purgeStagingData;
    }

    public S3DestinationConfig getS3DestinationConfig() {
        return s3DestinationConfig;
    }
}