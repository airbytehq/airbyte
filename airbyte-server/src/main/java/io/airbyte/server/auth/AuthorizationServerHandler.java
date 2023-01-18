/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.auth;

import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.channel.ChannelDuplexHandler;
import io.netty.channel.ChannelHandler.Sharable;
import io.netty.channel.ChannelHandlerContext;
import jakarta.inject.Singleton;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

/**
 * Custom Netty {@link ChannelDuplexHandler} that intercepts all operations to ensure that headers
 * required for authorization are populated prior to performing the security check.
 */
@Singleton
@Sharable
@Slf4j
public class AuthorizationServerHandler extends ChannelDuplexHandler {

  /**
   * Regular expression used to find the delimiter between HTTP headers and body in the string
   * representation of an HTTP request.
   */
  private static final String BLANK_LINE_REGEX = "(?m)^[ \t]*\r?\n";

  private static final String AIRBYTE_HEADER_PREFIX = "X-Airbyte-";

  /**
   * HTTP header that contains the connection ID for authorization purposes.
   */
  public static final String CONNECTION_ID_HEADER = AIRBYTE_HEADER_PREFIX + "Connection-Id";

  /**
   * HTTP header that contains the destination ID for authorization purposes.
   */
  public static final String DESTINATION_ID_HEADER = AIRBYTE_HEADER_PREFIX + "Destination-Id";

  /**
   * HTTP header that contains the job ID for authorization purposes.
   */
  public static final String JOB_ID_HEADER = AIRBYTE_HEADER_PREFIX + "Job-Id";

  /**
   * HTTP header that contains the operation ID for authorization purposes.
   */
  public static final String OPERATION_ID_HEADER = AIRBYTE_HEADER_PREFIX + "Operation-Id";

  /**
   * HTTP header that contains the source ID for authorization purposes.
   */
  public static final String SOURCE_ID_HEADER = AIRBYTE_HEADER_PREFIX + "Source-Id";

  /**
   * HTTP header that contains the source definition ID for authorization purposes.
   */
  public static final String SOURCE_DEFINITION_ID_HEADER = AIRBYTE_HEADER_PREFIX + "Source-Definition-Id";

  /**
   * HTTP header that contains the workspace ID for authorization purposes.
   */
  public static final String WORKSPACE_ID_HEADER = AIRBYTE_HEADER_PREFIX + "Workspace-Id";

  private final AirbyteHttpRequestFieldExtractor airbyteHttpRequestFieldExtractor;

  public AuthorizationServerHandler(final AirbyteHttpRequestFieldExtractor airbyteHttpRequestFieldExtractor) {
    this.airbyteHttpRequestFieldExtractor = airbyteHttpRequestFieldExtractor;
  }

  @Override
  public void channelRead(
                          final ChannelHandlerContext context,
                          final Object message) {

    Object updatedMessage = message;

    if (ByteBuf.class.isInstance(message)) {
      final ByteBuf content = ByteBuf.class.cast(message);
      ByteBuf updatedContent = content;

      final String originalContentAsString = StandardCharsets.UTF_8.decode(content.nioBuffer()).toString();
      final Optional<UUID> connectionId = airbyteHttpRequestFieldExtractor.extractConnectionId(originalContentAsString);
      final Optional<UUID> destinationId = airbyteHttpRequestFieldExtractor.extractDestinationId(originalContentAsString);
      final Optional<UUID> jobId = airbyteHttpRequestFieldExtractor.extractJobId(originalContentAsString);
      final Optional<UUID> operationId = airbyteHttpRequestFieldExtractor.extractOperationId(originalContentAsString);
      final Optional<UUID> sourceId = airbyteHttpRequestFieldExtractor.extractSourceId(originalContentAsString);
      final Optional<UUID> sourceDefinitionId = airbyteHttpRequestFieldExtractor.extractSourceDefinitionId(originalContentAsString);
      final Optional<UUID> workspaceId = airbyteHttpRequestFieldExtractor.extractWorkspaceId(originalContentAsString);

      if (connectionId.isPresent()) {
        updatedContent = Unpooled.wrappedBuffer(generateBufferWithHeader(CONNECTION_ID_HEADER, connectionId.get(), updatedContent.nioBuffer()));
      }
      if (destinationId.isPresent()) {
        updatedContent = Unpooled.wrappedBuffer(generateBufferWithHeader(DESTINATION_ID_HEADER, destinationId.get(), updatedContent.nioBuffer()));
      }
      if (jobId.isPresent()) {
        updatedContent = Unpooled.wrappedBuffer(generateBufferWithHeader(JOB_ID_HEADER, jobId.get(), updatedContent.nioBuffer()));
      }
      if (operationId.isPresent()) {
        updatedContent = Unpooled.wrappedBuffer(generateBufferWithHeader(OPERATION_ID_HEADER, operationId.get(), updatedContent.nioBuffer()));
      }
      if (sourceId.isPresent()) {
        updatedContent = Unpooled.wrappedBuffer(generateBufferWithHeader(SOURCE_ID_HEADER, sourceId.get(), updatedContent.nioBuffer()));
      }
      if (sourceDefinitionId.isPresent()) {
        updatedContent =
            Unpooled.wrappedBuffer(generateBufferWithHeader(SOURCE_DEFINITION_ID_HEADER, sourceDefinitionId.get(), updatedContent.nioBuffer()));
      }
      if (workspaceId.isPresent()) {
        updatedContent = Unpooled.wrappedBuffer(generateBufferWithHeader(WORKSPACE_ID_HEADER, workspaceId.get(), updatedContent.nioBuffer()));
      }

      updatedMessage = updatedContent;
    }

    context.fireChannelRead(updatedMessage);
  }

  private ByteBuffer generateBufferWithHeader(final String headerName, final Object headerValue, final ByteBuffer originalContent) {
    final String originalContentAsString = StandardCharsets.UTF_8.decode(originalContent).toString();
    final String updatedContent = originalContentAsString.replaceAll(BLANK_LINE_REGEX, headerName + ": " + headerValue.toString() + "\r\n\r\n");
    return ByteBuffer.wrap(updatedContent.getBytes(StandardCharsets.UTF_8));
  }

}
