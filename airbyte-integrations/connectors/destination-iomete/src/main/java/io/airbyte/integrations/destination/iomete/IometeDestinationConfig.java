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

    static final String DEFAULT_LAKEHOUSE_PORT = "443";
    static final String DEFAULT_DATABASE_SCHEMA = "default";
    static final boolean DEFAULT_PURGE_STAGING_DATA = true;
    static final boolean DEFAULT_SSL_CONNECTION = true;

    private final String lakehouseHostname;
    private final String lakehouseName;
    private final String lakehousePort;
    private final boolean isSSL;
    private final String accountNumber;
    private final String iometeUsername;
    private final String iometePassword;
    private final String databaseSchema;
    private final boolean purgeStagingData;
    private final S3DestinationConfig s3DestinationConfig;

    public IometeDestinationConfig(
            final String lakehouseHostname,
            final String lakehouseName,
            final String lakehousePort,
            final boolean isSSL,
            final String accountNumber,
            final String iometeUsername,
            final String iometePassword,
            final String databaseSchema,
            final boolean purgeStagingData,
            final S3DestinationConfig s3DestinationConfig) {
        this.lakehouseHostname = lakehouseHostname;
        this.lakehouseName = lakehouseName;
        this.lakehousePort = lakehousePort;
        this.isSSL = isSSL;
        this.accountNumber = accountNumber;
        this.iometeUsername = iometeUsername;
        this.iometePassword = iometePassword;
        this.databaseSchema = databaseSchema;
        this.purgeStagingData = purgeStagingData;
        this.s3DestinationConfig = s3DestinationConfig;
    }


    public static IometeDestinationConfig get(final JsonNode config) {
        IometeDestinationConnectionUrlResolver connectionUrl
                = IometeDestinationConnectionUrlResolver.create(config.get("connection_url").asText());
        return new IometeDestinationConfig(
                connectionUrl.lakehouseHostname,
                connectionUrl.lakehouseName,
                DEFAULT_LAKEHOUSE_PORT,
                config.has("ssl") ? config.get("ssl").asBoolean() : DEFAULT_SSL_CONNECTION,
                connectionUrl.accountNumber,
                config.get("iomete_username").asText(),
                config.get("iomete_password").asText(),
                config.has("database_schema") ? config.get("database_schema").asText() : DEFAULT_DATABASE_SCHEMA,
                isPurgeStagingData(config),
                getStaging(config.get("staging")));
    }

    public static S3DestinationConfig getStaging(final JsonNode staging) {
        final S3DestinationConfig.Builder builder = S3DestinationConfig.create(
            staging.get(S3Constants.S_3_BUCKET_NAME).asText(),
            staging.get(S3Constants.S_3_BUCKET_PATH).asText(),
            staging.get(S3Constants.S_3_BUCKET_REGION).asText())
            .withAccessKeyCredential(
                    staging.get(S3Constants.S_3_ACCESS_KEY_ID).asText(),
                    staging.get(S3Constants.S_3_SECRET_ACCESS_KEY).asText())
            .withFormatConfig(getDefaultParquetConfig());
        if (staging.has(S3Constants.FILE_NAME_PATTERN)) {
            builder.withFileNamePattern(staging.get(S3Constants.FILE_NAME_PATTERN).asText());
        }
        return builder.get();
    }

    private static S3ParquetFormatConfig getDefaultParquetConfig() {
        return new S3ParquetFormatConfig(new ObjectMapper().createObjectNode());
    }

    private static boolean isPurgeStagingData(final JsonNode config) {
        final JsonNode staging = config.get("staging");
        return staging.has("purge_staging_data")
                ? staging.get("purge_staging_data").asBoolean() : DEFAULT_PURGE_STAGING_DATA;
    }

    public String getLakehouseHostname() {
        return lakehouseHostname;
    }

    public String getLakehouseName() {
        return lakehouseName;
    }

    public String getLakehousePort() {
        return lakehousePort;
    }

    public boolean isSSL() {
        return isSSL;
    }

    public String getAccountNumber() {
        return accountNumber;
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