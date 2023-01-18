/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.auth;

import io.micronaut.core.util.StringUtils;
import jakarta.inject.Singleton;
import java.util.Optional;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import lombok.extern.slf4j.Slf4j;

/**
 * Utility class that facilitates the extraction of values from HTTP request POST bodies.
 */
@Singleton
@Slf4j
public class AirbyteHttpRequestFieldExtractor {

  private static final String DOT_ALL = ".*";

  private static final String FIELD_SEPARATOR = "\s*:\s*";

  private static final String QUOTE_PATTERN = "\"";

  /**
   * Regular expression that finds a UUID value in a string.
   */
  private static final String UUID_REGEX = "([0-9a-fA-F]{8}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{12})";

  /**
   * Name of the field in HTTP request bodies that contains the connection ID value.
   */
  private static final String CONNECTION_ID_FIELD_NAME = "connectionId";

  /**
   * Regular expression that finds a connection ID UUID value in an HTTP request.
   */
  private static final String CONNECTION_ID_REGEX =
      DOT_ALL + QUOTE_PATTERN + CONNECTION_ID_FIELD_NAME + FIELD_SEPARATOR + UUID_REGEX + QUOTE_PATTERN + DOT_ALL;

  /**
   * Compiled regular expression pattern used to extract a connection ID value from an HTTP request.
   */
  private static final Pattern CONNECTION_ID_PATTERN = Pattern.compile(CONNECTION_ID_REGEX);

  /**
   * Name of the field in HTTP request bodies that contains the destination ID value.
   */
  private static final String DESTINATION_ID_FIELD_NAME = "destinationId";

  /**
   * Regular expression that finds a destination ID UUID value in an HTTP request.
   */
  private static final String DESTINATION_ID_REGEX =
      DOT_ALL + QUOTE_PATTERN + DESTINATION_ID_FIELD_NAME + QUOTE_PATTERN + FIELD_SEPARATOR + QUOTE_PATTERN + UUID_REGEX + QUOTE_PATTERN + DOT_ALL;

  /**
   * Compiled regular expression pattern used to extract a destination ID value from an HTTP request.
   */
  private static final Pattern DESTINATION_ID_PATTERN = Pattern.compile(DESTINATION_ID_REGEX);

  /**
   * Name of the field in HTTP request bodies that contains the job ID value.
   */
  private static final String JOB_ID_FIELD_NAME = "id";

  /**
   * Regular expression that finds a job ID UUID value in an HTTP request.
   */
  private static final String JOB_ID_REGEX =
      DOT_ALL + QUOTE_PATTERN + JOB_ID_FIELD_NAME + QUOTE_PATTERN + FIELD_SEPARATOR + QUOTE_PATTERN + UUID_REGEX + QUOTE_PATTERN + DOT_ALL;

  /**
   * Compiled regular expression pattern used to extract a job ID value from an HTTP request.
   */
  private static final Pattern JOB_ID_PATTERN = Pattern.compile(JOB_ID_REGEX);

  /**
   * Name of the field in HTTP request bodies that contains the operation ID value.
   */
  private static final String OPERATION_ID_FIELD_NAME = "id";

  /**
   * Regular expression that finds a operation ID UUID value in an HTTP request.
   */
  private static final String OPERATION_ID_REGEX =
      DOT_ALL + QUOTE_PATTERN + OPERATION_ID_FIELD_NAME + QUOTE_PATTERN + FIELD_SEPARATOR + QUOTE_PATTERN + UUID_REGEX + QUOTE_PATTERN + DOT_ALL;

  /**
   * Compiled regular expression pattern used to extract an operation ID value from an HTTP request.
   */
  private static final Pattern OPERATION_ID_PATTERN = Pattern.compile(OPERATION_ID_REGEX);

  /**
   * Name of the field in HTTP request bodies that contains the source ID value.
   */
  private static final String SOURCE_ID_FIELD_NAME = "id";

  /**
   * Regular expression that finds a source ID UUID value in an HTTP request.
   */
  private static final String SOURCE_ID_REGEX =
      DOT_ALL + QUOTE_PATTERN + SOURCE_ID_FIELD_NAME + QUOTE_PATTERN + FIELD_SEPARATOR + QUOTE_PATTERN + UUID_REGEX + QUOTE_PATTERN + DOT_ALL;

  /**
   * Compiled regular expression pattern used to extract a source ID value from an HTTP request.
   */
  private static final Pattern SOURCE_ID_PATTERN = Pattern.compile(SOURCE_ID_REGEX);

  /**
   * Name of the field in HTTP request bodies that contains the source definition ID value.
   */
  private static final String SOURCE_DEFINITION_ID_FIELD_NAME = "id";

  /**
   * Regular expression that finds a source definition ID UUID value in an HTTP request.
   */
  private static final String SOURCE_DEFINITION_ID_REGEX = DOT_ALL + QUOTE_PATTERN + SOURCE_DEFINITION_ID_FIELD_NAME + QUOTE_PATTERN + FIELD_SEPARATOR
      + QUOTE_PATTERN + UUID_REGEX + QUOTE_PATTERN + DOT_ALL;

  /**
   * Compiled regular expression pattern used to extract a source definition ID value from an HTTP
   * request.
   */
  private static final Pattern SOURCE_DEFINITION_ID_PATTERN = Pattern.compile(SOURCE_DEFINITION_ID_REGEX);

  /**
   * Name of the field in HTTP request bodies that contains the workspace ID value.
   */
  private static final String WORKSPACE_ID_FIELD_NAME = "workspaceId";

  /**
   * Regular expression that finds a workspace ID UUID value in an HTTP request.
   */
  private static final String WORKSPACE_ID_REGEX =
      DOT_ALL + QUOTE_PATTERN + WORKSPACE_ID_FIELD_NAME + QUOTE_PATTERN + FIELD_SEPARATOR + QUOTE_PATTERN + UUID_REGEX + QUOTE_PATTERN + DOT_ALL;

  /**
   * Compiled regular expression pattern used to extract a workspace ID value from an HTTP request.
   */
  private static final Pattern WORKSPACE_ID_PATTERN = Pattern.compile(WORKSPACE_ID_REGEX);

  public Optional<UUID> extractConnectionId(final String content) {
    return extractId(content, CONNECTION_ID_PATTERN, CONNECTION_ID_FIELD_NAME);
  }

  public Optional<UUID> extractDestinationId(final String content) {
    return extractId(content, DESTINATION_ID_PATTERN, DESTINATION_ID_FIELD_NAME);
  }

  public Optional<UUID> extractJobId(final String content) {
    return extractId(content, JOB_ID_PATTERN, JOB_ID_FIELD_NAME);
  }

  public Optional<UUID> extractOperationId(final String content) {
    return extractId(content, OPERATION_ID_PATTERN, OPERATION_ID_FIELD_NAME);
  }

  public Optional<UUID> extractSourceId(final String content) {
    return extractId(content, SOURCE_ID_PATTERN, SOURCE_ID_FIELD_NAME);
  }

  public Optional<UUID> extractSourceDefinitionId(final String content) {
    return extractId(content, SOURCE_DEFINITION_ID_PATTERN, SOURCE_DEFINITION_ID_FIELD_NAME);
  }

  public Optional<UUID> extractWorkspaceId(final String content) {
    return extractId(content, WORKSPACE_ID_PATTERN, WORKSPACE_ID_FIELD_NAME);
  }

  public Optional<UUID> extractId(final String content, final Pattern idPattern, final String idFieldName) {
    if (StringUtils.isNotEmpty(content) && content.contains(idFieldName)) {
      final Matcher matcher = idPattern.matcher(content);
      if (matcher.find()) {
        return Optional.of(UUID.fromString(matcher.group(1)));
      }
    }

    return Optional.empty();
  }

}
