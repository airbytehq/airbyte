package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.InsertAllResponse;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobStatus;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.helpers.CheckPermissionHelper;
import io.airbyte.integrations.destination.bigquery.service.CheckService;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.micronaut.context.annotation.Primary;
import io.micronaut.context.annotation.Property;
import io.micronaut.context.env.Environment;
import io.micronaut.test.annotation.MockBean;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@MicronautTest(environments = {Environment.TEST})
public class CheckServiceTest {

    @Inject
    CheckService checkService;

    BigQuery mockBigQuery = mock(BigQuery.class);
    CheckPermissionHelper mockCheckPermissionHelper = mock(CheckPermissionHelper.class);

    @MockBean
    BigQuery mockBigQuery() { return mockBigQuery; }

    @MockBean
    @Primary
    CheckPermissionHelper mockCheckPermissionHelper() { return mockCheckPermissionHelper; }

    @Test
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".project-id", value = "check-test")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".dataset-id", value = "check-test")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".dataset-location", value = "US")
    void testCheck() throws InterruptedException {
        final TableId tableId = TableId.of("check-test", "check-test", "check-test");
        final Table table = mock(Table.class);
        final Dataset dataset = mock(Dataset.class);
        final InsertAllResponse insertAllResponse = mock(InsertAllResponse.class);
        final Job job = mock(Job.class);
        final JobInfo jobInfo = mock(JobInfo.class);
        final JobStatus jobStatus = mock(JobStatus.class);
        when(dataset.getLocation()).thenReturn("US");
        when(job.getStatus()).thenReturn(jobStatus);
        when(job.waitFor()).thenReturn(job);
        when(jobInfo.getStatus()).thenReturn(jobStatus);
        when(table.getTableId()).thenReturn(tableId);
        when(mockBigQuery.create(any(DatasetInfo.class))).thenReturn(dataset);
        when(mockBigQuery.create(any(JobInfo.class))).thenReturn(job);
        when(mockBigQuery.create(any(TableInfo.class))).thenReturn(table);
        when(mockBigQuery.insertAll(any())).thenReturn(insertAllResponse);

        assertDoesNotThrow(() -> {
            final AirbyteConnectionStatus status = checkService.check();
            assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, status.getStatus());
        });
    }

    @Test
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".project-id", value = "check-test")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".dataset-id", value = "check-test")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".dataset-location", value = "US")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.method", value = "GCS Staging")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.gcs-bucket-name", value = "bucket-name")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.gcs-bucket-path", value = "bucket-path")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.credential.credential-type", value = "HMAC_KEY")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.credential.hmac-key-access-id", value = "id")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.credential.hmac-key-secret", value = "secret")
    void testCheckGcsUploadingMethod() throws InterruptedException {
        final TableId tableId = TableId.of("check-test", "check-test", "check-test");
        final Table table = mock(Table.class);
        final Dataset dataset = mock(Dataset.class);
        final InsertAllResponse insertAllResponse = mock(InsertAllResponse.class);
        final Job job = mock(Job.class);
        final JobInfo jobInfo = mock(JobInfo.class);
        final JobStatus jobStatus = mock(JobStatus.class);
        when(dataset.getLocation()).thenReturn("US");
        when(job.getStatus()).thenReturn(jobStatus);
        when(job.waitFor()).thenReturn(job);
        when(jobInfo.getStatus()).thenReturn(jobStatus);
        when(table.getTableId()).thenReturn(tableId);
        when(mockBigQuery.create(any(DatasetInfo.class))).thenReturn(dataset);
        when(mockBigQuery.create(any(JobInfo.class))).thenReturn(job);
        when(mockBigQuery.create(any(TableInfo.class))).thenReturn(table);
        when(mockBigQuery.insertAll(any())).thenReturn(insertAllResponse);

        assertDoesNotThrow(() -> {
            final AirbyteConnectionStatus status = checkService.check();
            assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, status.getStatus());
        });
    }

    @Test
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".project-id", value = "check-test")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".dataset-id", value = "check-test")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".dataset-location", value = "US")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.method", value = "GCS Staging")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.gcs-bucket-name", value = "bucket-name")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.gcs-bucket-path", value = "bucket-path")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.credential.credential-type", value = "HMAC_KEY")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.credential.hmac-key-access-id", value = "id")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.credential.hmac-key-secret", value = "secret")
    void testCheckGcsUploadingMethodError() throws InterruptedException, IOException {
        final TableId tableId = TableId.of("check-test", "check-test", "check-test");
        final Table table = mock(Table.class);
        final Dataset dataset = mock(Dataset.class);
        final InsertAllResponse insertAllResponse = mock(InsertAllResponse.class);
        final Job job = mock(Job.class);
        final JobInfo jobInfo = mock(JobInfo.class);
        final JobStatus jobStatus = mock(JobStatus.class);
        when(dataset.getLocation()).thenReturn("US");
        when(job.getStatus()).thenReturn(jobStatus);
        when(job.waitFor()).thenReturn(job);
        when(jobInfo.getStatus()).thenReturn(jobStatus);
        when(table.getTableId()).thenReturn(tableId);
        when(mockBigQuery.create(any(DatasetInfo.class))).thenReturn(dataset);
        when(mockBigQuery.create(any(JobInfo.class))).thenReturn(job);
        when(mockBigQuery.create(any(TableInfo.class))).thenReturn(table);
        when(mockBigQuery.insertAll(any())).thenReturn(insertAllResponse);
        doThrow(new IOException("test")).when(mockCheckPermissionHelper).testUpload(any());

        assertDoesNotThrow(() -> {
            final AirbyteConnectionStatus status = checkService.check();
            assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
        });
    }

    @Test
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".project-id", value = "check-test")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".dataset-id", value = "check-test")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".dataset-location", value = "EU")
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX + ".loading-method.method", value = "Standard")
    void testCheckDatasetLocationMismatch() throws InterruptedException {
        final TableId tableId = TableId.of("check-test", "check-test", "check-test");
        final Table table = mock(Table.class);
        final Dataset dataset = mock(Dataset.class);
        final InsertAllResponse insertAllResponse = mock(InsertAllResponse.class);
        final Job job = mock(Job.class);
        final JobInfo jobInfo = mock(JobInfo.class);
        final JobStatus jobStatus = mock(JobStatus.class);
        when(dataset.getLocation()).thenReturn("US");
        when(job.getStatus()).thenReturn(jobStatus);
        when(job.waitFor()).thenReturn(job);
        when(jobInfo.getStatus()).thenReturn(jobStatus);
        when(table.getTableId()).thenReturn(tableId);
        when(mockBigQuery.create(any(DatasetInfo.class))).thenReturn(dataset);
        when(mockBigQuery.create(any(JobInfo.class))).thenReturn(job);
        when(mockBigQuery.create(any(TableInfo.class))).thenReturn(table);
        when(mockBigQuery.insertAll(any())).thenReturn(insertAllResponse);

        final ConfigErrorException e = assertThrows(ConfigErrorException.class, () -> {
            final AirbyteConnectionStatus status = checkService.check();
            assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
        });
        assertEquals("Actual dataset location doesn't match to location from config", e.getMessage());
    }
}
