package io.airbyte.cdk.integrations.base.config;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.micronaut.context.annotation.ConfigurationProperties;
import io.micronaut.core.util.StringUtils;

@ConfigurationProperties("airbyte.connector.catalog")
public class AirbyteConfiguredCatalog {

    String configured;

    public ConfiguredAirbyteCatalog getConfiguredCatalog() {
        return StringUtils.isNotEmpty(configured) ? Jsons.deserialize(configured, ConfiguredAirbyteCatalog.class) :
                new ConfiguredAirbyteCatalog();
    }
}
