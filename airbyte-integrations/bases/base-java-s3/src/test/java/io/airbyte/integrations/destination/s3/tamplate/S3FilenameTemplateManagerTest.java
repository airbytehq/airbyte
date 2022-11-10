/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.tamplate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mockStatic;

import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.template.S3FilenameTemplateManager;
import io.airbyte.integrations.destination.s3.template.S3FilenameTemplateParameterObject;
import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.util.TimeZone;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

class S3FilenameTemplateManagerTest {

  private final S3FilenameTemplateManager s3FilenameTemplateManager = new S3FilenameTemplateManager();

  @Test
  @DisplayName("Should replace the date placeholder with the current date in the format YYYY-MM-DD")
  void testDatePlaceholder()
      throws IOException {
    final String fileNamePattern = "test-{date}";
    final String fileExtension = "csv";
    final String partId = "1";

    final String actual = s3FilenameTemplateManager
        .applyPatternToFilename(S3FilenameTemplateParameterObject
            .builder()
            .objectPath("")
            .fileNamePattern(fileNamePattern)
            .fileExtension(fileExtension)
            .partId(partId).build());

    final DateFormat defaultDateFormat = new SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING);
    defaultDateFormat.setTimeZone(TimeZone.getTimeZone("UTC"));

    long currentTimeInMillis = Instant.now().toEpochMilli();

    final String expected = "test-" + defaultDateFormat.format(currentTimeInMillis);
    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("Should replace the timestamp placeholder with the current timestamp in milliseconds")
  void testTimestampPlaceholder()
      throws IOException {
    final String fileNamePattern = "test-{timestamp}.csv";

    final Clock clock = Clock.fixed(Instant.ofEpochMilli(1657110148000L), ZoneId.of("UTC"));
    final Instant instant = Instant.now(clock);

    try (final MockedStatic<Instant> mocked = mockStatic(Instant.class)) {
      mocked.when(Instant::now).thenReturn(instant);
      final String actual = s3FilenameTemplateManager
          .applyPatternToFilename(S3FilenameTemplateParameterObject.builder()
              .objectPath("")
              .fileNamePattern(fileNamePattern)
              .fileExtension("csv")
              .partId("1")
              .build());

      assertEquals("test-1657110148000.csv", actual);
    }
  }

  @Test
  @DisplayName("Should sanitize the string and adapt it to applicable S3 format")
  void testIfFilenameTemplateStringWasSanitized() throws IOException {
    final String fileNamePattern = "  te  st.csv  ";
    final String actual = s3FilenameTemplateManager
        .applyPatternToFilename(S3FilenameTemplateParameterObject.builder()
            .objectPath("")
            .fileNamePattern(fileNamePattern)
            .fileExtension("csv")
            .partId("1")
            .build());

    assertEquals("te__st.csv", actual);
  }

}
