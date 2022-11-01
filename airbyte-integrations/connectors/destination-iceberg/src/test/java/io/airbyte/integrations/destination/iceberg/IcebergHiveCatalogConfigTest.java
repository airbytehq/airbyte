package io.airbyte.integrations.destination.iceberg;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.when;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.AmazonS3Exception;
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest;
import com.amazonaws.services.s3.model.InitiateMultipartUploadResult;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import com.amazonaws.services.s3.model.UploadPartRequest;
import com.amazonaws.services.s3.model.UploadPartResult;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.iceberg.config.FormatConfig;
import io.airbyte.integrations.destination.iceberg.config.HiveCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.IcebergCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.IcebergCatalogConfigFactory;
import io.airbyte.integrations.destination.iceberg.config.S3Config;
import io.airbyte.integrations.destination.iceberg.config.credential.S3AccessKeyCredentialConfig;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.io.IOException;
import lombok.extern.slf4j.Slf4j;
import org.apache.iceberg.Table;
import org.apache.iceberg.TableScan;
import org.apache.iceberg.catalog.Catalog;
import org.apache.iceberg.data.IcebergGenerics;
import org.apache.iceberg.data.IcebergGenerics.ScanBuilder;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@Slf4j
class IcebergHiveCatalogConfigTest {

    private AmazonS3 s3;
    private IcebergCatalogConfigFactory factory;

    @BeforeAll
    static void staticSetup() {
        mockStatic(IcebergGenerics.class);
    }

    @BeforeEach
    void setup() throws IOException {
        s3 = mock(AmazonS3.class);
        final InitiateMultipartUploadResult uploadResult = mock(InitiateMultipartUploadResult.class);
        final UploadPartResult uploadPartResult = mock(UploadPartResult.class);
        when(s3.uploadPart(any(UploadPartRequest.class))).thenReturn(uploadPartResult);
        when(s3.initiateMultipartUpload(any(InitiateMultipartUploadRequest.class))).thenReturn(uploadResult);

        TableScan tableScan = mock(TableScan.class);
        when(tableScan.schema()).thenReturn(null);
        Table tempTable = mock(Table.class);
        when(tempTable.newScan()).thenReturn(tableScan);
        ScanBuilder scanBuilder = mock(ScanBuilder.class);
        when(scanBuilder.build()).thenReturn(new EmptyIterator());
        when(IcebergGenerics.read(tempTable)).thenReturn(scanBuilder);

        Catalog catalog = mock(Catalog.class);
        when(catalog.createTable(any(), any())).thenReturn(tempTable);
        when(catalog.dropTable(any())).thenReturn(true);

        IcebergCatalogConfig config = new HiveCatalogConfig("thrift://fake-thrift-uri") {
            @Override
            public Catalog genCatalog() {
                return catalog;
            }
        };
        config.setStorageConfig(S3Config.builder()
            .warehouseUri("fake-bucket")
            .bucketRegion("fake-region")
            .endpoint("fake-endpoint")
            .endpointWithSchema("https://fake-endpoint")
            .accessKeyId("fake-accessKeyId")
            .secretKey("fake-secretAccessKey")
            .credentialConfig(new S3AccessKeyCredentialConfig("fake-accessKeyId", "fake-secretAccessKey"))
            .s3Client(s3)
            .build());
        config.setFormatConfig(new FormatConfig("Parquet"));
        config.setDefaultDatabase("default");

        factory = new IcebergCatalogConfigFactory() {
            @Override
            public IcebergCatalogConfig fromJsonNodeConfig(final @NotNull JsonNode jsonConfig) {
                return config;
            }
        };
    }

    /**
     * Test that check will fail if IAM user does not have listObjects permission
     */
    @Test
    public void checksHiveCatalogWithoutS3ListObjectPermission() {
        final IcebergDestination destinationFail = new IcebergDestination(factory);
        doThrow(new AmazonS3Exception("Access Denied")).when(s3).listObjects(any(ListObjectsRequest.class));
        final AirbyteConnectionStatus status = destinationFail.check(null);
        log.info("status={}", status);
        assertEquals(Status.FAILED, status.getStatus(), "Connection check should have failed");
        assertTrue(status.getMessage().indexOf("Access Denied") > 0, "Connection check returned wrong failure message");
    }


    /**
     * Test that check will succeed when IAM user has all required permissions
     */
    @Test
    public void checksHiveCatalogWithS3ListObjectPermission() {
        final IcebergDestination destinationSuccess = new IcebergDestination(factory);
        final AirbyteConnectionStatus status = destinationSuccess.check(null);
        assertEquals(Status.SUCCEEDED, status.getStatus(), "Connection check should have succeeded");
    }

}