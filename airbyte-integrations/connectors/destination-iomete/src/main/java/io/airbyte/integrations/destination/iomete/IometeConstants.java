package io.airbyte.integrations.destination.iomete;

import io.airbyte.db.factory.DatabaseDriver;

import java.util.Set;

public class IometeConstants {
    public static final String IOMETE_DRIVER_CLASS = DatabaseDriver.IOMETE.getDriverClassName();
    public static final String IOMETE_URL_FORMAT_STRING = DatabaseDriver.IOMETE.getUrlFormatString();
    public static final Set<String> DEFAULT_TBL_PROPERTIES = Set.of(
            "'write.format.default' = 'parquet'");

}