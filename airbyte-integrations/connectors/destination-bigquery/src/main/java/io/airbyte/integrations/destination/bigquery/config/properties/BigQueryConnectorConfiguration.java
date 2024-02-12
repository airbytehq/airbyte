package io.airbyte.integrations.destination.bigquery.config.properties;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.cdk.integrations.base.config.ConnectorConfiguration;
import io.micronaut.context.annotation.ConfigurationBuilder;
import io.micronaut.context.annotation.ConfigurationProperties;
import org.springframework.util.StringUtils;

import java.util.Optional;

@ConfigurationProperties("airbyte.connector.config")
@JsonIgnoreProperties({"loadingMethodBuilder", "rawNamespace"})
public class BigQueryConnectorConfiguration implements ConnectorConfiguration {

    private static final String DEFAULT_DATASET_LOCATION = "US";

    @JsonProperty("big_query_client_buffer_size_mb")
    Integer bigQueryClientBufferSizeMb;
    @JsonProperty("credentials_json")
    String credentialsJson;
    @JsonProperty("dataset_id")
    String datasetId;
    @JsonProperty("dataset_location")
    String datasetLocation;
    @JsonProperty("disable_type_dedupe")
    boolean disableTypeDedupe;
    @JsonProperty("project_id")
    String projectId;
    @JsonProperty("raw_data_dataset")
    String rawDataDataset;
    @JsonProperty("transformation_priority")
    String transformationPriority;

    @ConfigurationBuilder(prefixes = "with", configurationPrefix = "loading_method")
    protected LoadingMethodConfiguration.Builder loadingMethodBuilder = new LoadingMethodConfiguration.Builder();

    public Integer getBigQueryClientBufferSizeMb() {
        return bigQueryClientBufferSizeMb;
    }

    public String getCredentialsJson() {
        return credentialsJson;
    }

    public String getDatasetId() {
        return datasetId;
    }

    public String getDatasetLocation() {
        return StringUtils.hasText(datasetLocation) ? datasetLocation : DEFAULT_DATASET_LOCATION;
    }

    public boolean isDisableTypeDedupe() {
        return disableTypeDedupe;
    }

    public String getProjectId() {
        return projectId;
    }

    public String getRawDataDataset() {
        return rawDataDataset;
    }

    public String getTransformationPriority() {
        return transformationPriority;
    }

    @JsonProperty("loading_method")
    public LoadingMethodConfiguration getLoadingMethod() {
        return loadingMethodBuilder.build();
    }

    @Override
    public Optional<String> getRawNamespace() {
        return Optional.ofNullable(getRawDataDataset());
    }
}
