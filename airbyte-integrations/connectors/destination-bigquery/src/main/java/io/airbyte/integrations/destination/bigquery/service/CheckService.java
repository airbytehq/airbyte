package io.airbyte.integrations.destination.bigquery.service;

import com.amazonaws.services.s3.model.AmazonS3Exception;
import com.codepoetics.protonpack.StreamUtils;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.UploadingMethod;
import io.airbyte.integrations.destination.bigquery.config.properties.BigQueryConnectorConfiguration;
import io.airbyte.integrations.destination.bigquery.config.properties.LoadingMethodConfiguration;
import io.airbyte.integrations.destination.bigquery.helpers.CheckPermissionHelper;
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import jakarta.inject.Singleton;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

import static io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage;

@Singleton
public class CheckService {

    private static final Logger LOGGER = LoggerFactory.getLogger(CheckService.class);

    private static final String EXPECTED_ROLES = "storage.multipartUploads.abort, storage.multipartUploads.create, "
            + "storage.objects.create, storage.objects.delete, storage.objects.get, storage.objects.list";

    private static final List<String> REQUIRED_PERMISSIONS = List.of(
            "storage.multipartUploads.abort",
            "storage.multipartUploads.create",
            "storage.objects.create",
            "storage.objects.delete",
            "storage.objects.get",
            "storage.objects.list");

    private final BigQuery bigQuery;
    private final BigQueryConnectorConfiguration configuration;
    private final BigQueryUtils bigQueryUtils;
    private final CheckPermissionHelper checkPermissionHelper;

    public CheckService(final BigQuery bigQuery,
                        final BigQueryConnectorConfiguration configuration,
                        final BigQueryUtils bigQueryUtils,
                        final CheckPermissionHelper checkPermissionHelper) {
        this.bigQuery = bigQuery;
        this.configuration = configuration;
        this.bigQueryUtils = bigQueryUtils;
        this.checkPermissionHelper = checkPermissionHelper;
    }

    public AirbyteConnectionStatus check() {
        final String datasetId = bigQueryUtils.getDatasetId(configuration);
        final String datasetLocation = bigQueryUtils.getDatasetLocation(configuration);
        final UploadingMethod uploadingMethod = bigQueryUtils.getLoadingMethod(configuration);

        bigQueryUtils.checkHasCreateAndDeleteDatasetRole(bigQuery, datasetId, datasetLocation);

        final Dataset dataset = bigQueryUtils.getOrCreateDataset(bigQuery, datasetId, datasetLocation);
        if (!dataset.getLocation().equals(datasetLocation)) {
            throw new ConfigErrorException("Actual dataset location doesn't match to location from config");
        }
        final QueryJobConfiguration queryConfig = QueryJobConfiguration
                .newBuilder(String.format("SELECT * FROM `%s.INFORMATION_SCHEMA.TABLES` LIMIT 1;", datasetId))
                .setUseLegacySql(false)
                .build();

        if (UploadingMethod.GCS.equals(uploadingMethod)) {
            final AirbyteConnectionStatus status = checkGcsPermission(configuration);
            if (!status.getStatus().equals(AirbyteConnectionStatus.Status.SUCCEEDED)) {
                return status;
            }
        }

        final ImmutablePair<Job, String> result = bigQueryUtils.executeQuery(bigQuery, queryConfig);
        if (result.getLeft() != null) {
            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
        } else {
            throw new ConfigErrorException(result.getRight());
        }
    }

    /**
     * This method does two checks: 1) permissions related to the bucket, and 2) the ability to create
     * and delete an actual file. The latter is important because even if the service account may have
     * the proper permissions, the HMAC keys can only be verified by running the actual GCS check.
     */
    private AirbyteConnectionStatus checkGcsPermission(final BigQueryConnectorConfiguration configuration) {
        final LoadingMethodConfiguration loadingMethod = configuration.getLoadingMethod();
        final String bucketName = loadingMethod.getGcsBucketName();
        final List<String> missingPermissions = new ArrayList<>();

        try {
            final GoogleCredentials credentials = bigQueryUtils.getServiceAccountCredentials(configuration);
            final Storage storage = StorageOptions.newBuilder()
                    .setProjectId(configuration.getProjectId())
                    .setCredentials(credentials)
                    .setHeaderProvider(bigQueryUtils.getHeaderProvider())
                    .build().getService();
            final List<Boolean> permissionsCheckStatusList = storage.testIamPermissions(bucketName, REQUIRED_PERMISSIONS);

            missingPermissions.addAll(StreamUtils
                    .zipWithIndex(permissionsCheckStatusList.stream())
                    .filter(i -> !i.getValue())
                    .map(i -> REQUIRED_PERMISSIONS.get(Math.toIntExact(i.getIndex())))
                    .toList());

            final JsonNode gcsJsonNodeConfig = bigQueryUtils.getGcsJsonNodeConfig(configuration);
            return checkPermissions(gcsJsonNodeConfig);
        } catch (final Exception e) {
            final StringBuilder message = new StringBuilder("Cannot access the GCS bucket.");
            if (!missingPermissions.isEmpty()) {
                message.append(" The following permissions are missing on the service account: ")
                        .append(String.join(", ", missingPermissions))
                        .append(".");
            }
            message.append(" Please make sure the service account can access the bucket path, and the HMAC keys are correct.");

            LOGGER.error(message.toString(), e);
            throw new ConfigErrorException("Could not access the GCS bucket with the provided configuration.\n", e);
        }
    }

    private AirbyteConnectionStatus checkPermissions(final JsonNode config) {
        try {
            final GcsDestinationConfig destinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config);
            checkPermissionHelper.testUpload(destinationConfig);
            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
        } catch (final AmazonS3Exception e) {
            LOGGER.error("Exception attempting to access the Gcs bucket", e);
            final String message = getErrorMessage(e.getErrorCode(), 0, e.getMessage(), e);
            AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
            return new AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
                    .withMessage(message);
        } catch (final Exception e) {
            LOGGER.error("Exception attempting to access the Gcs bucket: {}. Please make sure you account has all of these roles: " + EXPECTED_ROLES, e);
            AirbyteTraceMessageUtility.emitConfigErrorTrace(e, e.getMessage());
            return new AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
                    .withMessage("Could not connect to the Gcs bucket with the provided configuration. \n" + e
                            .getMessage());
        }
    }
}
