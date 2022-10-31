package io.airbyte.integrations.destination.iceberg;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.AmazonS3Exception;
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest;
import com.amazonaws.services.s3.model.InitiateMultipartUploadResult;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import com.amazonaws.services.s3.model.UploadPartRequest;
import com.amazonaws.services.s3.model.UploadPartResult;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.iceberg.config.HiveCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.IcebergCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.IcebergCatalogConfigFactory;
import io.airbyte.integrations.destination.iceberg.config.S3Config;
import io.airbyte.integrations.destination.iceberg.config.credential.S3AccessKeyCredentialConfig;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.io.IOException;
import lombok.extern.slf4j.Slf4j;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@Slf4j
class IcebergDestinationTest {

    private AmazonS3 s3;
    private IcebergCatalogConfig config;

    private IcebergCatalogConfigFactory factory;

    @BeforeEach
    void setup() throws IOException {
        s3 = mock(AmazonS3.class);
        final InitiateMultipartUploadResult uploadResult = mock(InitiateMultipartUploadResult.class);
        final UploadPartResult uploadPartResult = mock(UploadPartResult.class);
        when(s3.uploadPart(any(UploadPartRequest.class))).thenReturn(uploadPartResult);
        when(s3.initiateMultipartUpload(any(InitiateMultipartUploadRequest.class))).thenReturn(uploadResult);

        config = new HiveCatalogConfig("fake-thrift-uri", "default");
        config.setStorageConfig(S3Config.builder()
            .warehouseUri("fake-bucket")
            .bucketRegion("fake-region")
            .endpoint("fake-endpoint")
            .credentialConfig(new S3AccessKeyCredentialConfig("fake-accessKeyId", "fake-secretAccessKey"))
            .s3Client(s3)
            .build());

        factory = new IcebergCatalogConfigFactory() {
            @Override
            public IcebergCatalogConfig fromJsonNodeConfig(final @NotNull JsonNode config) {
                return IcebergDestinationTest.this.config;
            }
        };
    }

    /**
     * Test that check will fail if IAM user does not have listObjects permission
     */
    @Test
    public void checksS3WithoutListObjectPermission() {
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
    public void checksS3WithListObjectPermission() {
        final IcebergDestination destinationSuccess = new IcebergDestination(factory);
        final AirbyteConnectionStatus status = destinationSuccess.check(null);
        assertEquals(Status.SUCCEEDED, status.getStatus(), "Connection check should have succeeded");
    }
}