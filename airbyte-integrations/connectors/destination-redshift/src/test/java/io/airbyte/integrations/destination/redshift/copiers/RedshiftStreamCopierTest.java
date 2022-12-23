/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.copiers;

import static java.util.Comparator.comparing;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.amazonaws.services.s3.AmazonS3Client;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopyConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class RedshiftStreamCopierTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStreamCopierTest.class);

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  // The full path would be something like
  // "fake-namespace/fake_stream/2021_12_09_1639077474000_e549e712-b89c-4272-9496-9690ba7f973e.csv"
  // The namespace and stream have their hyphens replaced by underscores. Not super clear that that's
  // actually required.
  // 2021_12_09_1639077474000 is generated from the timestamp. It's followed by a random UUID, in case
  // we need to create multiple files.
  private static final String EXPECTED_OBJECT_BEGINNING = "fake-bucketPath/fake_namespace/fake_stream/2021_12_09_1639077474000_";
  private static final String EXPECTED_OBJECT_ENDING = ".csv";

  // equivalent to Thu, 09 Dec 2021 19:17:54 GMT
  private static final Timestamp UPLOAD_TIME = Timestamp.from(Instant.ofEpochMilli(1639077474000L));

  private AmazonS3Client s3Client;
  private JdbcDatabase db;
  private SqlOperations sqlOperations;
  private RedshiftStreamCopier copier;

  @BeforeEach
  public void setup() {
    s3Client = mock(AmazonS3Client.class, RETURNS_DEEP_STUBS);
    db = mock(JdbcDatabase.class);
    sqlOperations = mock(SqlOperations.class);

    final S3DestinationConfig s3Config = S3DestinationConfig.create(
        "fake-bucket",
        "fake-bucketPath",
        "fake-region")
        .withEndpoint("fake-endpoint")
        .withAccessKeyCredential("fake-access-key-id", "fake-secret-access-key")
        .get();

    copier = new RedshiftStreamCopier(
        // In reality, this is normally a UUID - see CopyConsumerFactory#createWriteConfigs
        "fake-staging-folder",
        "fake-schema",
        s3Client,
        db,
        new S3CopyConfig(true, s3Config),
        new ExtendedNameTransformer(),
        sqlOperations,
        UPLOAD_TIME,
        new ConfiguredAirbyteStream()
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withName("fake-stream")
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
                .withNamespace("fake-namespace")));
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
          final boolean startsCorrectly = path.startsWith("fake-bucketPath/fake-staging-folder/fake-schema/");
          final boolean endsCorrectly = path.endsWith(".manifest");
          // Make sure that we have a valid UUID
          manifestUuid.set(path.replaceFirst("^fake-bucketPath/fake-staging-folder/fake-schema/", "").replaceFirst(".manifest$", ""));
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
        }));

    verify(db).execute(String.format(
        """
        COPY fake-schema.%s FROM 's3://fake-bucket/fake-bucketPath/fake-staging-folder/fake-schema/%s.manifest'
        CREDENTIALS 'aws_access_key_id=fake-access-key-id;aws_secret_access_key=fake-secret-access-key'
        CSV REGION 'fake-region' TIMEFORMAT 'auto'
        STATUPDATE OFF
        MANIFEST;""",
        copier.getTmpTableName(),
        manifestUuid.get()));
  }

  private static boolean isManifestEntryCorrect(final JsonNode entry, final String expectedFilename) {
    final String url = entry.get("url").asText();
    final boolean mandatory = entry.get("mandatory").asBoolean();

    return ("s3://fake-bucket/" + expectedFilename).equals(url) && mandatory;
  }

}
