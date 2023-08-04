package io.airbyte.integrations.destination.iceberg;

import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import org.mockito.MockedStatic;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageException;
import org.apache.iceberg.data.IcebergGenerics;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import lombok.extern.slf4j.Slf4j;
import java.io.IOException;

@Slf4j
class BigLakeCatalogConfigTest {

  private static MockedStatic<IcebergGenerics> mockedIcebergGenerics;

  private Storage cloudStorage;

  @BeforeAll
  static void staticSetup() {
    BigLakeCatalogConfigTest.mockedIcebergGenerics = mockStatic(IcebergGenerics.class);
  }

  @AfterAll
  static void staticStop() {
    BigLakeCatalogConfigTest.mockedIcebergGenerics.close();
  }

  @BeforeEach
  void setup() throws IOException {
    cloudStorage = mock(Storage.class);
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
    public void checksBigLakeWithoutGCPListObjectPermission () {
      final IcebergDestination destinationFail = new IcebergDestination(factory);
      doThrow(new StorageException(401, "Access Denied")).when(cloudStorage).listObjects(any(ListObjectsRequest.class));
      final AirbyteConnectionStatus status = destinationFail.check(null);
      log.info("status={}", status);
      assertEquals(Status.FAILED, status.getStatus(), "Connection check should have failed");
      assertTrue(status.getMessage().contains("Access Denied"), "Connection check returned wrong failure message");
    }

  }

