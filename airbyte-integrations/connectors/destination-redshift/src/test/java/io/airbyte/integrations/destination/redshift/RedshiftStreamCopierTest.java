package io.airbyte.integrations.destination.redshift;

import static java.util.Collections.singletonList;
import static java.util.Comparator.comparing;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockConstruction;
import static org.mockito.Mockito.verify;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3Client;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedConstruction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class RedshiftStreamCopierTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStreamCopierTest.class);

  private static final int PART_SIZE = 5;
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  // The full path would be something like "fake-namespace/fake_stream/2021_12_09_1639077474000_e549e712-b89c-4272-9496-9690ba7f973e.csv"
  // The namespace and stream have their hyphens replaced by underscores. Not super clear that that's actually required.
  // 2021_12_09_1639077474000 is generated from the timestamp. It's followed by a random UUID, in case we need to create multiple files.
  private static final String EXPECTED_OBJECT_BEGINNING = "fake-bucketPath/fake_namespace/fake_stream/2021_12_09_1639077474000_";
  private static final String EXPECTED_OBJECT_ENDING = ".csv";

  // equivalent to Thu, 09 Dec 2021 19:17:54 GMT
  private static final Timestamp UPLOAD_TIME = Timestamp.from(Instant.ofEpochMilli(1639077474000L));

  private AmazonS3Client s3Client;
  private JdbcDatabase db;
  private SqlOperations sqlOperations;
  private RedshiftStreamCopier copier;

  private MockedConstruction<StreamTransferManager> streamTransferManagerMockedConstruction;
  private List<ByteArrayOutputStream> outputStreams;

  @BeforeEach
  public void setup() {
    s3Client = mock(AmazonS3Client.class);
    db = mock(JdbcDatabase.class);
    sqlOperations = mock(SqlOperations.class);

    outputStreams = new ArrayList<>();

    // This is basically RETURNS_SELF, except with getMultiPartOutputStreams configured correctly.
    // Other non-void methods (e.g. toString()) will return null.
    streamTransferManagerMockedConstruction = mockConstruction(
        StreamTransferManager.class,
        (mock, context) -> {
          doReturn(mock).when(mock).numUploadThreads(anyInt());
          doReturn(mock).when(mock).queueCapacity(anyInt());
          doReturn(mock).when(mock).partSize(anyLong());
          doReturn(mock).when(mock).numStreams(anyInt());

          // We can't write a fake MultiPartOutputStream, because it doesn't have a public constructor.
          // So instead, we'll build a mock that captures its data into a ByteArrayOutputStream.
          final MultiPartOutputStream stream = mock(MultiPartOutputStream.class);
          doReturn(singletonList(stream)).when(mock).getMultiPartOutputStreams();
          final ByteArrayOutputStream capturer = new ByteArrayOutputStream();
          outputStreams.add(capturer);
          doAnswer(invocation -> {
            capturer.write((int) invocation.getArgument(0));
            return null;
          }).when(stream).write(anyInt());
          doAnswer(invocation -> {
            capturer.write(invocation.getArgument(0));
            return null;
          }).when(stream).write(any(byte[].class));
          doAnswer(invocation -> {
            capturer.write(invocation.getArgument(0), invocation.getArgument(1), invocation.getArgument(2));
            return null;
          }).when(stream).write(any(byte[].class), anyInt(), anyInt());
        }
    );

    copier = new RedshiftStreamCopier(
        // In reality, this is normally a UUID - see CopyConsumerFactory#createWriteConfigs
        "fake-staging-folder",
        "fake-schema",
        s3Client,
        db,
        new S3DestinationConfig(
            "fake-endpoint",
            "fake-bucket",
            "fake-bucketPath",
            "fake-region",
            "fake-access-key-id",
            "fake-secret-access-key",
            PART_SIZE,
            null
        ),
        new ExtendedNameTransformer(),
        sqlOperations,
        UPLOAD_TIME,
        new ConfiguredAirbyteStream()
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withName("fake-stream")
                .withNamespace("fake-namespace")
            )
    );
  }

  @AfterEach
  public void teardown() {
    streamTransferManagerMockedConstruction.close();
  }

  @Test
  public void createSequentialStagingFiles_when_multipleFilesRequested() {
    // When we call prepareStagingFile() the first time, it should create exactly one upload manager. The next (MAX_PARTS_PER_FILE - 1) invocations
    // should reuse that same upload manager.
    for (var i = 0; i < RedshiftStreamCopier.MAX_PARTS_PER_FILE; i++) {
      final String file = copier.prepareStagingFile();
      checkObjectName(file);
      final List<StreamTransferManager> firstManagers = streamTransferManagerMockedConstruction.constructed();
      final StreamTransferManager firstManager = firstManagers.get(0);
      verify(firstManager).partSize(PART_SIZE);
      assertEquals(1, firstManagers.size());
    }

    // Now that we've hit the MAX_PARTS_PER_FILE, we should start a new upload
    final String secondFile = copier.prepareStagingFile();
    checkObjectName(secondFile);
    final List<StreamTransferManager> secondManagers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager secondManager = secondManagers.get(1);
    verify(secondManager).partSize(PART_SIZE);
    assertEquals(2, secondManagers.size());
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedSuccessfully() throws Exception {
    copier.prepareStagingFile();

    copier.closeStagingUploader(false);

    final List<StreamTransferManager> managers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager manager = managers.get(0);
    verify(manager).complete();
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedFailingly() throws Exception {
    copier.prepareStagingFile();

    copier.closeStagingUploader(true);

    final List<StreamTransferManager> managers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager manager = managers.get(0);
    verify(manager).abort();
  }

  @Test
  public void deletesStagingFiles() throws Exception {
    final String file = copier.prepareStagingFile();
    doReturn(true).when(s3Client).doesObjectExist("fake-bucket", file);

    copier.removeFileAndDropTmpTable();

    verify(s3Client).deleteObject("fake-bucket", file);
  }

  @Test
  public void writesContentsCorrectly() throws Exception {
    final String file1 = copier.prepareStagingFile();
    for (int i = 0; i < RedshiftStreamCopier.MAX_PARTS_PER_FILE - 1; i++) {
      copier.prepareStagingFile();
    }
    copier.write(
        UUID.fromString("f6767f7d-ce1e-45cc-92db-2ad3dfdd088e"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"foo\": 73}"))
            .withEmittedAt(1234L),
        file1
    );
    copier.write(
        UUID.fromString("2b95a13f-d54f-4370-a712-1c7bf2716190"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"bar\": 84}"))
            .withEmittedAt(2345L),
        file1
    );

    final String file2 = copier.prepareStagingFile();
    copier.write(
        UUID.fromString("24eba873-de57-4901-9e1e-2393334320fb"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"asd\": 95}"))
            .withEmittedAt(3456L),
        file2
    );

    copier.closeStagingUploader(false);

    // carriage returns are required b/c RFC4180 requires it :(
    assertEquals(
        String.format(
            """
                f6767f7d-ce1e-45cc-92db-2ad3dfdd088e,"{""foo"":73}",%s\r
                2b95a13f-d54f-4370-a712-1c7bf2716190,"{""bar"":84}",%s\r
                """,
            Timestamp.from(Instant.ofEpochMilli(1234)),
            Timestamp.from(Instant.ofEpochMilli(2345))
        ),
        outputStreams.get(0).toString(StandardCharsets.UTF_8));
    assertEquals(
        String.format(
            "24eba873-de57-4901-9e1e-2393334320fb,\"{\"\"asd\"\":95}\",%s\r\n",
            Timestamp.from(Instant.ofEpochMilli(3456))
        ),
        outputStreams.get(1).toString(StandardCharsets.UTF_8)
    );
  }

  @Test
  public void copiesCorrectFilesToTable() throws SQLException {
    // Generate two files
    final String file1 = copier.prepareStagingFile();
    for (int i = 0; i < RedshiftStreamCopier.MAX_PARTS_PER_FILE - 1; i++) {
      copier.prepareStagingFile();
    }
    final String file2 = copier.prepareStagingFile();
    final List<String> expectedFiles = List.of(file1, file2).stream().sorted().toList();

    copier.copyStagingFileToTemporaryTable();

    final AtomicReference<String> manifestUuid = new AtomicReference<>();
    verify(s3Client).putObject(
        eq("fake-bucket"),
        argThat(path -> {
          final boolean startsCorrectly = path.startsWith("fake-staging-folder/fake-schema/");
          final boolean endsCorrectly = path.endsWith(".manifest");
          // Make sure that we have a valid UUID
          manifestUuid.set(path.replaceFirst("^fake-staging-folder/fake-schema/", "").replaceFirst(".manifest$", ""));
          UUID.fromString(manifestUuid.get());

          return startsCorrectly && endsCorrectly;
        }),
        (String) argThat(manifestStr -> {
          try {
            final JsonNode manifest = OBJECT_MAPPER.readTree((String) manifestStr);
            final List<JsonNode> entries = Lists.newArrayList(manifest.get("entries").elements()).stream()
                .sorted(comparing(entry -> entry.get("url").asText())).toList();

            boolean entriesAreCorrect = true;
            for (int i = 0; i < 2; i++) {
              final String expectedFilename = expectedFiles.get(i);
              final JsonNode manifestEntry = entries.get(i);
              entriesAreCorrect &= isManifestEntryCorrect(manifestEntry, expectedFilename);
              if (!entriesAreCorrect) {
                LOGGER.error("Invalid entry: {}", manifestEntry);
              }
            }

            return entriesAreCorrect && entries.size() == 2;
          } catch (final JsonProcessingException e) {
            throw new RuntimeException(e);
          }
        })
    );

    verify(db).execute(String.format(
        """
            COPY fake-schema.%s FROM 's3://fake-bucket/fake-staging-folder/fake-schema/%s.manifest'
            CREDENTIALS 'aws_access_key_id=fake-access-key-id;aws_secret_access_key=fake-secret-access-key'
            CSV REGION 'fake-region' TIMEFORMAT 'auto'
            STATUPDATE OFF
            MANIFEST;""",
        copier.getTmpTableName(),
        manifestUuid.get()
    ));
  }

  private static String checkObjectName(final String objectName) {
    final String errorMessage = "Object was actually " + objectName;

    assertTrue(objectName.startsWith(EXPECTED_OBJECT_BEGINNING), errorMessage);
    assertTrue(objectName.endsWith(EXPECTED_OBJECT_ENDING), errorMessage);

    // Remove the beginning and ending, which _should_ leave us with just a UUID
    final String uuidMaybe = objectName
        // "^" == start of string
        .replaceFirst("^" + EXPECTED_OBJECT_BEGINNING, "")
        // "$" == end of string
        .replaceFirst(EXPECTED_OBJECT_ENDING + "$", "");
    assertDoesNotThrow(() -> UUID.fromString(uuidMaybe), errorMessage + "; supposed UUID was " + uuidMaybe);

    return uuidMaybe;
  }

  private static boolean isManifestEntryCorrect(final JsonNode entry, final String expectedFilename) {
    final String url = entry.get("url").asText();
    final boolean mandatory = entry.get("mandatory").asBoolean();

    return ("s3://fake-bucket/" + expectedFilename).equals(url) && mandatory;
  }
}
