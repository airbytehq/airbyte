package io.airbyte.integrations.destination.iomete;

import io.airbyte.db.factory.DatabaseDriver;

import java.util.Set;

public class IometeConstants {
    public static final String IOMETE_DRIVER_CLASS = DatabaseDriver.IOMETE.getDriverClassName();
    public static final String IOMETE_URL_FORMAT_STRING = DatabaseDriver.IOMETE.getUrlFormatString();
    public static final Set<String> DEFAULT_TBL_PROPERTIES = Set.of(
            "'write.format.default' = 'parquet'");

    public static final String AIRBYTE_PROTOCOL = "airbyte://";
    public static final String LAKEHOUSE_HOSTNAME_EXAMPLE = "iomete.com";
    public static final String ACCOUNT_NUMBER_EXAMPLE = "000000000000";
    public static final String DEFAULT_LAKEHOUSE_NAME = "default";

}