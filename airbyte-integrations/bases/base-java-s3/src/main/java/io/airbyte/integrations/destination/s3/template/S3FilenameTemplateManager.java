/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.template;

import static java.util.Optional.ofNullable;
import static org.apache.commons.lang3.StringUtils.EMPTY;

import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.TimeZone;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.text.StringSubstitutor;
import org.apache.commons.text.lookup.StringLookupFactory;

/**
 * This class is responsible for building the filename template based on user input, see
 * file_name_pattern in the specification of connector currently supported only S3 staging.
 */
public class S3FilenameTemplateManager {

  private static final String UTC = "UTC";
  private final StringSubstitutor stringSubstitutor;

  public S3FilenameTemplateManager() {
    stringSubstitutor = new StringSubstitutor();
  }

  public String applyPatternToFilename(final S3FilenameTemplateParameterObject parameterObject)
      throws IOException {
    // sanitize fileFormat
    final String sanitizedFileFormat = parameterObject
        .getFileNamePattern()
        .trim()
        .replaceAll(" ", "_");

    stringSubstitutor.setVariableResolver(
        StringLookupFactory.INSTANCE.mapStringLookup(fillTheMapWithDefaultPlaceHolders(sanitizedFileFormat, parameterObject)));
    stringSubstitutor.setVariablePrefix("{");
    stringSubstitutor.setVariableSuffix("}");
    return ofNullable(parameterObject.getObjectPath()).orElse(EMPTY) + stringSubstitutor.replace(sanitizedFileFormat);
  }

  private Map<String, String> fillTheMapWithDefaultPlaceHolders(final String stringToReplaceWithPlaceholder,
                                                                final S3FilenameTemplateParameterObject parameterObject) {

    final long currentTimeMillis = Instant.now().toEpochMilli();

    final Map<String, String> valuesMap = processExtendedPlaceholder(currentTimeMillis, stringToReplaceWithPlaceholder);

    final DateFormat defaultDateFormat = new SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING);
    defaultDateFormat.setTimeZone(TimeZone.getTimeZone(UTC));

    // here we set default values for supported placeholders.
    valuesMap.put("date", ofNullable(defaultDateFormat.format(currentTimeMillis)).orElse(EMPTY));
    valuesMap.put("timestamp", ofNullable(String.valueOf(currentTimeMillis)).orElse(EMPTY));
    valuesMap.put("sync_id", ofNullable(System.getenv("WORKER_JOB_ID")).orElse(EMPTY));
    valuesMap.put("format_extension", ofNullable(parameterObject.getFileExtension()).orElse(EMPTY));
    valuesMap.put("part_number", ofNullable(parameterObject.getPartId()).orElse(EMPTY));

    return valuesMap;
  }

  /**
   * By extended placeholders we assume next types: {date:yyyy_MM}, {timestamp:millis},
   * {timestamp:micro}, etc Limited combinations are supported by the method see the method body.
   *
   * @param stringToReplaceWithPlaceholder - string where the method will search for extended
   *        placeholders
   * @return map with prepared placeholders.
   */
  private Map<String, String> processExtendedPlaceholder(final long currentTimeMillis, final String stringToReplaceWithPlaceholder) {
    final Map<String, String> valuesMap = new HashMap<>();

    final Pattern pattern = Pattern.compile("\\{(date:.+?|timestamp:.+?)\\}");
    final Matcher matcher = pattern.matcher(stringToReplaceWithPlaceholder);

    while (matcher.find()) {
      final String[] splitByColon = matcher.group(1).split(":");
      switch (splitByColon[0].toLowerCase(Locale.ROOT)) {
        case "date" -> {
          final DateFormat dateFormat = new SimpleDateFormat(splitByColon[1]);
          dateFormat.setTimeZone(TimeZone.getTimeZone("UTC"));
          valuesMap.put(matcher.group(1), dateFormat.format(currentTimeMillis));
        }
        case "timestamp" -> {
          switch (splitByColon[1]) {
            case "millis" -> {
              valuesMap.put(matcher.group(1), String.valueOf(currentTimeMillis));
            }
            case "micro" -> {
              valuesMap.put(matcher.group(1), String.valueOf(convertToMicrosecondsRepresentation(currentTimeMillis)));
            }
          }
        }
      }
    }
    return valuesMap;
  }

  private long convertToMicrosecondsRepresentation(final long milliSeconds) {
    // The time representation in microseconds is equal to the milliseconds multiplied by 1,000.
    return milliSeconds * 1000;
  }

}
