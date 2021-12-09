package io.airbyte.integrations.destination.s3.csv;

import static java.util.Collections.singletonList;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockConstruction;
import static org.mockito.Mockito.verify;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedConstruction;

class S3CsvWriterTest {

  private static final int PART_SIZE = 7;
  // equivalent to Thu, 09 Dec 2021 19:17:54 GMT
  private static final Timestamp UPLOAD_TIME = Timestamp.from(Instant.ofEpochMilli(1639077474000L));
  private static final int UPLOAD_THREADS = 8;
  private static final int QUEUE_CAPACITY = 9;

  public static final String EXPECTED_OBJECT_KEY = "fake-bucketPath/fake_namespace/fake_stream/2021_12_09_1639077474000fake-suffix.csv";

  private S3CsvWriter writer;

  private MockedConstruction<StreamTransferManager> streamTransferManagerMockedConstruction;
  private List<StreamTransferManagerArguments> streamTransferManagerConstructorArguments;

  // TODO when we're on java 17, this should be a record class
  private static class StreamTransferManagerArguments {

    public final String bucket;
    public final String object;

    public StreamTransferManagerArguments(final String bucket, final String object) {
      this.bucket = bucket;
      this.object = object;
    }
  }

  @BeforeEach
  public void setup() throws IOException {
    streamTransferManagerConstructorArguments = new ArrayList<>();
    // This is basically RETURNS_SELF, except with getMultiPartOutputStreams configured correctly.
    // Other non-void methods (e.g. toString()) will return null.
    streamTransferManagerMockedConstruction = mockConstruction(
        StreamTransferManager.class,
        (mock, context) -> {
          // Mockito doesn't seem to provide an easy way to actually retrieve these arguments later on, so manually store them on construction.
          // _PowerMockito_ does, but I didn't want to set up that additional dependency.
          final List<?> arguments = context.arguments();
          streamTransferManagerConstructorArguments.add(new StreamTransferManagerArguments((String) arguments.get(0), (String) arguments.get(1)));

          doReturn(mock).when(mock).numUploadThreads(anyInt());
          doReturn(mock).when(mock).numStreams(anyInt());
          doReturn(mock).when(mock).queueCapacity(anyInt());
          doReturn(mock).when(mock).partSize(anyLong());
          doReturn(singletonList(mock(MultiPartOutputStream.class))).when(mock).getMultiPartOutputStreams();
        }
    );

    // The part size is configured in the format config. This field is only used by S3StreamCopier.
    final S3DestinationConfig config = new S3DestinationConfig(
        "fake-endpoint",
        "fake-bucket",
        "fake-bucketPath",
        "fake-region",
        "fake-access-key-id",
        "fake-secret-access-key",
        // The part size is configured in the format config. This field is only used by S3StreamCopier.
        null,
        new S3CsvFormatConfig(Flattening.NO, (long) PART_SIZE)
    );
    final ConfiguredAirbyteStream configuredStream = new ConfiguredAirbyteStream()
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withStream(new AirbyteStream()
            .withName("fake-stream")
            .withNamespace("fake-namespace")
        );
    final AmazonS3 s3Client = mock(AmazonS3Client.class);

    writer = new S3CsvWriter(
        config,
        s3Client,
        configuredStream,
        UPLOAD_TIME,
        UPLOAD_THREADS,
        QUEUE_CAPACITY,
        "fake-suffix"
    );
  }

  @AfterEach
  public void teardown() {
    streamTransferManagerMockedConstruction.close();
  }

  @Test
  public void generatesCorrectObjectKey_when_created() {
    final String objectKey = writer.getObjectKey();

    // The namespace and stream have their hyphens replaced by underscores. Not super clear that that's actually required.
    // 2021_12_09_1639077474000 is generated from the timestamp. The final _0 is hardcoded in BaseS3Writer; similarly unclear that it's required.
    assertEquals(EXPECTED_OBJECT_KEY, objectKey);
  }

  @Test
  public void createsExactlyOneUpload() {
    assertEquals(1, streamTransferManagerMockedConstruction.constructed().size());

    assertEquals("fake-bucket", streamTransferManagerConstructorArguments.get(0).bucket);
    assertEquals(EXPECTED_OBJECT_KEY, streamTransferManagerConstructorArguments.get(0).object);
  }

  @Test
  public void respectsUploadSettings() {
    final StreamTransferManager manager = streamTransferManagerMockedConstruction.constructed().get(0);

    verify(manager).partSize(PART_SIZE);
    verify(manager).numUploadThreads(UPLOAD_THREADS);
    verify(manager).queueCapacity(QUEUE_CAPACITY);
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedSuccessfully() throws Exception {
    writer.close(false);

    final List<StreamTransferManager> managers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager manager = managers.get(0);
    verify(manager).complete();
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedFailingly() throws Exception {
    writer.close(true);

    final List<StreamTransferManager> managers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager manager = managers.get(0);
    verify(manager).abort();
  }
}
