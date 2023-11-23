package io.airbyte.integrations.source_performance;

/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
import static io.airbyte.protocol.models.AirbyteMessage.Type.RECORD;
import static io.airbyte.protocol.models.AirbyteMessage.Type.STATE;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.logging.MdcScope.Builder;
import io.airbyte.commons.protocol.DefaultProtocolSerializer;
import io.airbyte.commons.protocol.ProtocolSerializer;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.protos.AirbyteRecordMessage;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.internal.AirbyteSource;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.internal.HeartbeatMonitor;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;
import java.nio.file.Path;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import javax.annotation.CheckForNull;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Default implementation of {@link AirbyteSource}.
 */
public class DefaultAirbyteSourceProto {

  private static final Logger LOGGER = LoggerFactory.getLogger(io.airbyte.workers.internal.DefaultAirbyteSource.class);

  private static final Duration GRACEFUL_SHUTDOWN_DURATION = Duration.of(1, ChronoUnit.MINUTES);
  static final Set<Integer> IGNORED_EXIT_CODES = Set.of(
      0, // Normal exit
      143 // SIGTERM
  );

  public static final MdcScope.Builder CONTAINER_LOG_MDC_BUILDER = new Builder()
      .setLogPrefix("source")
      .setPrefixColor(Color.BLUE_BACKGROUND);

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;
  private final ProtocolSerializer protocolSerializer;
  private final HeartbeatMonitor heartbeatMonitor;

  private Process sourceProcess = null;
  private Iterator<io.airbyte.protocol.protos.AirbyteMessage> messageIterator = null;
  private Integer exitValue = null;
  private final boolean featureFlagLogConnectorMsgs;

  public DefaultAirbyteSourceProto(IntegrationLauncher integrationLauncher, FeatureFlags featureFlags, HeartbeatMonitor heartbeatMonitor) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory(CONTAINER_LOG_MDC_BUILDER), heartbeatMonitor, new DefaultProtocolSerializer(),
        featureFlags);
  }

  public DefaultAirbyteSourceProto(final IntegrationLauncher integrationLauncher,
                                   final AirbyteStreamFactory streamFactory,
                                   final HeartbeatMonitor heartbeatMonitor,
                                   final ProtocolSerializer protocolSerializer,
                                   final FeatureFlags featureFlags) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
    this.protocolSerializer = protocolSerializer;
    this.heartbeatMonitor = heartbeatMonitor;
    this.featureFlagLogConnectorMsgs = featureFlags.logConnectorMessages();
  }

  public void start(final WorkerSourceConfig sourceConfig, final Path jobRoot) throws Exception {
    Preconditions.checkState(sourceProcess == null);

    sourceProcess = integrationLauncher.read(jobRoot,
        WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
        Jsons.serialize(sourceConfig.getSourceConnectionConfiguration()),
        WorkerConstants.SOURCE_CATALOG_JSON_FILENAME,
        protocolSerializer.serialize(sourceConfig.getCatalog()),
        sourceConfig.getState() == null ? null : WorkerConstants.INPUT_STATE_JSON_FILENAME,
        // TODO We should be passing a typed state here and use the protocolSerializer
        sourceConfig.getState() == null ? null : Jsons.serialize(sourceConfig.getState().getState()));
    // stdout logs are logged elsewhere since stdout also contains data
    LineGobbler.gobble(sourceProcess.getErrorStream(), LOGGER::error, "airbyte-source", CONTAINER_LOG_MDC_BUILDER);

    logInitialStateAsJSON(sourceConfig);

    // read protobuf from the source process
    final List<Type> acceptedMessageTypes = List.of(Type.RECORD, STATE, Type.TRACE, Type.CONTROL);
    // now we need to generate protobuf messages from the source process
    // this needs to take in a buffered reader and return an iterator of protobuf message
    messageIterator = new ProtoIterator(sourceProcess.getInputStream());
  }

  @Slf4j
  private static class ProtoIterator extends AbstractIterator<io.airbyte.protocol.protos.AirbyteMessage> {

    private final ByteArrayOutputStream buffer = new ByteArrayOutputStream(); // this has an inbuilt buffer.
    private final InputStream stream;

    public ProtoIterator(InputStream stream) {
      super();
      this.stream = stream;
    }

    @CheckForNull
    @Override
    protected io.airbyte.protocol.protos.AirbyteMessage computeNext() {
      boolean isProtobufMessage = false;
      int nextByte;

      while (true) {
        try {
          if ((nextByte = stream.read()) == -1)
            break;
        } catch (IOException e) {
          throw new RuntimeException(e);
        }

        // whenever it's a protobuf message, print the buffer.
        if (nextByte == 0) {
          if (buffer.size() > 0) {
//            log.info(String.valueOf(buffer));
            buffer.reset();
          }
          isProtobufMessage = true;
        } else {
          // store in the buffer and continue.
          buffer.write(nextByte);
          continue;
        }

        // after that we process the protobuf message.
        if (isProtobufMessage) {
          try {
            io.airbyte.protocol.protos.AirbyteMessage message = io.airbyte.protocol.protos.AirbyteMessage.parseDelimitedFrom(stream);
            if (message != null) {
              return message;
            }
          } catch (IOException e) {
            // Handle parsing error
            System.out.println(e);
          } finally {
            isProtobufMessage = false;
          }
        }
      }
      return endOfData();
    }

  }

  @VisibleForTesting
  static boolean shouldBeat(final AirbyteMessage.Type airbyteMessageType) {
    return airbyteMessageType == STATE || airbyteMessageType == RECORD;
  }

  public boolean isFinished() {
    Preconditions.checkState(sourceProcess != null);

    /*
     * As this check is done on every message read, it is important for this operation to be efficient.
     * Short circuit early to avoid checking the underlying process. note: hasNext is blocking.
     */
    return !messageIterator.hasNext() && !sourceProcess.isAlive();
  }

  public int getExitValue() throws IllegalStateException {
    Preconditions.checkState(sourceProcess != null, "Source process is null, cannot retrieve exit value.");
    Preconditions.checkState(!sourceProcess.isAlive(), "Source process is still alive, cannot retrieve exit value.");

    if (exitValue == null) {
      exitValue = sourceProcess.exitValue();
    }

    return exitValue;
  }

  public Optional<io.airbyte.protocol.protos.AirbyteMessage> attemptRead() {
    Preconditions.checkState(sourceProcess != null);

    return Optional.ofNullable(messageIterator.hasNext() ? messageIterator.next() : null);
  }

  public void close() throws Exception {
    if (sourceProcess == null) {
      LOGGER.debug("Source process already exited");
      return;
    }

    LOGGER.debug("Closing source process");
    WorkerUtils.gentleClose(
        sourceProcess,
        GRACEFUL_SHUTDOWN_DURATION.toMillis(),
        TimeUnit.MILLISECONDS);

    if (sourceProcess.isAlive() || !IGNORED_EXIT_CODES.contains(getExitValue())) {
      final String message = sourceProcess.isAlive() ? "Source has not terminated " : "Source process exit with code " + getExitValue();
      throw new WorkerException(message + ". This warning is normal if the job was cancelled.");
    }
  }

  public void cancel() throws Exception {
    LOGGER.info("Attempting to cancel source process...");

    if (sourceProcess == null) {
      LOGGER.info("Source process no longer exists, cancellation is a no-op.");
    } else {
      LOGGER.info("Source process exists, cancelling...");
      WorkerUtils.cancelProcess(sourceProcess);
      LOGGER.info("Cancelled source process!");
    }
  }

  private void logInitialStateAsJSON(final WorkerSourceConfig sourceConfig) {
    if (!featureFlagLogConnectorMsgs) {
      return;
    }

    if (sourceConfig.getState() == null) {
      LOGGER.info("source starting state | empty");
      return;
    }

    LOGGER.info("source starting state | " + Jsons.serialize(sourceConfig.getState().getState()));
  }

  private static void readFromInput(PipedInputStream inputStream) throws IOException {
    ByteArrayOutputStream buffer = new ByteArrayOutputStream(); // this has an inbuilt buffer.
    boolean isProtobufMessage = false;
    int nextByte;
    while ((nextByte = inputStream.read()) != -1) {
      // whenever it's a protobuf message or a next line, we need to print the buffer.
      if (nextByte == 0) {
        if (buffer.size() > 0) {
          System.out.println(buffer);
          buffer.reset();
        }
        isProtobufMessage = true;
      } else {
        // store in the buffer and continue.
        buffer.write(nextByte);
        continue;
      }

      // after that we process the protobuf message.
      if (isProtobufMessage) {
        System.out.println("=== Processing protobuf message");
        try {
          io.airbyte.protocol.protos.AirbyteMessage message = io.airbyte.protocol.protos.AirbyteMessage.parseDelimitedFrom(inputStream);
          if (message != null) {
            switch (message.getMessageCase()) {
              case RECORD:
                System.out.println("Received Record Message: " + message.getRecord().getStream());
                break;
              case STATE:
                System.out.println("Received State Message: " + message.getState().getData());
                break;
              case TRACE:
                System.out.println("Received Trace Message: " + message.getTrace());
                break;
              case CONTROL:
                System.out.println("Received Control Message: " + message.getControl().getType());
                break;
              default:
                System.out.println("Received Unknown Message: " + message.getMessageCase());
            }

            System.out.println("Received Message: " + message.getMessageCase());
          }
        } catch (IOException e) {
          // Handle parsing error
          System.out.println(e);
        } finally {
          isProtobufMessage = false;
        }
      }
    }
  }

  public static void main(String[] args) throws IOException {
    // EXAMPLE WRITING AND READING FROM PROTOBUF
    var msgs = List.of(
        AirbyteRecordMessage.newBuilder().setStream("a").build(),
        AirbyteRecordMessage.newBuilder().setStream("b").build(),
        AirbyteRecordMessage.newBuilder().setStream("c").build());

    // write them to an input stream
    var outputStream = new PipedOutputStream();
    var inputStream = new PipedInputStream(outputStream);

    msgs.forEach(msg -> {
      try {
        outputStream.write(new byte[] {0});
        io.airbyte.protocol.protos.AirbyteMessage.newBuilder()
            .setRecord(msg).build().writeDelimitedTo(outputStream);
        outputStream.write("\n".getBytes(Charsets.UTF_8));
        outputStream.write("random garbage \n".getBytes(Charsets.UTF_8));
        outputStream.write(Jsons.serialize("random json garbage").getBytes(Charsets.UTF_8));
      } catch (IOException e) {
        e.printStackTrace();
      }
    });
    outputStream.close();

    // consume them from the output stream

    // readFromInput(inputStream);
    new ProtoIterator(inputStream).forEachRemaining(System.out::println);

  }

}
