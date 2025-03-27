/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import static io.airbyte.integrations.source.e2e_test.DummyIterator.MAX_RECORDS;

import com.fasterxml.jackson.core.util.MinimalPrettyPrinter;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.SequenceWriter;
import com.google.common.collect.Iterators;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.*;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.*;
import io.netty.bootstrap.Bootstrap;
import io.netty.channel.ChannelFuture;
import io.netty.channel.ChannelOption;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.nio.NioSocketChannel;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class DummySource extends BaseConnector implements Source {

  public static final Integer THREADS = 10;

  public static void main(final String[] args) throws Exception {
    try {
      final CliParse integrationCliParser = new CliParse();
      final IntegrationConfig parse = integrationCliParser.parse(args);

      final DummySource source = new DummySource();

      switch (parse.getCommand()) {
        case SPEC, DISCOVER, CHECK -> {
          new IntegrationRunner(source).run(args);
        }
        case READ -> {
          System.out.println("Running read operation...");
          // readWithSerialization();
          readWithoutSerialization();
          // sendDataNoSerialization();
          System.out.println("Finished running read operation");
        }

        case WRITE -> {}
      }
    } catch (final Exception e) {
      e.printStackTrace();
      System.exit(1);
    }
    System.exit(0);
  }

  private static void readWithSerialization() {
    System.out.println("Read with serialization:");
    final List<CompletableFuture<?>> futures = new ArrayList<>();
    try (ExecutorService executor = Executors.newFixedThreadPool(THREADS)) {
      try (AutoCloseableIterator<AirbyteMessage> iterator = new DummyIterator()) {
        final Iterator<List<AirbyteMessage>> partitions = Iterators.partition(iterator, Long.valueOf(MAX_RECORDS / THREADS).intValue());
        while (partitions.hasNext()) {
          final List<AirbyteMessage> partition = partitions.next();
          futures.add(CompletableFuture.runAsync(() -> {
            System.out.println("Connecting to Container Orchestrator on thread " + Thread.currentThread().getName() + "...");
            try (Socket socket = new Socket("localhost", 9090)) {
              final BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), Charset.defaultCharset()));
              try (SequenceWriter seqWriter = DummyIterator.OBJECT_MAPPER
                  .writerFor(AirbyteMessage.class)
                  .with(new MinimalPrettyPrinter(System.lineSeparator()))
                  .writeValues(writer)) {
                partition.forEach(message -> {
                  try {
                    seqWriter.write(message);
                    writer.flush();
                  } catch (Exception e) {
                    throw new RuntimeException(e);
                  }
                });
              } catch (final Exception e) {
                throw new RuntimeException(e);
              } finally {
                try {
                  // Ensure all data is flushed at the end.
                  writer.flush();
                } catch (final Exception e) {
                  throw new RuntimeException(e);
                }
              }
            } catch (Exception e) {
              throw new RuntimeException(e);
            } finally {
              System.out.println("Connection on thread " + Thread.currentThread().getName() + " complete.");
            }
          }, executor));
        }
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).get();
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }
  }

  private static void readWithoutSerialization() {
    System.out.println("Read without serialization:");
    final List<CompletableFuture<?>> futures = new ArrayList<>();
    try (ExecutorService executor = Executors.newFixedThreadPool(THREADS)) {
      try (AutoCloseableIterator<String> iterator = new NoSerializationIterator()) {
        final Iterator<List<String>> partitions = Iterators.partition(iterator, Long.valueOf(MAX_RECORDS / THREADS).intValue());
        while (partitions.hasNext()) {
          final List<String> partition = partitions.next();
          futures.add(CompletableFuture.runAsync(() -> {
            System.out.println("Connecting to Container Orchestrator on thread " + Thread.currentThread().getName() + "...");
            try (SocketChannel socketChannel = SocketChannel.open(new InetSocketAddress("localhost", 9090))) {
              partition.forEach(message -> {
                try {
                  sendMessage(message, socketChannel);
                } catch (IOException e) {
                  throw new RuntimeException(e);
                }
              });
              // try (Socket socket = new Socket("localhost", 9090)) {
              // try (OutputStream outputStream = socket.getOutputStream()) {
              //
              // partition.forEach(message -> {
              // try {
              // sendMessage(message, outputStream);
              // } catch (final Exception e) {
              // throw new RuntimeException(e);
              // }
              // });
              // }
            } catch (final Exception e) {
              throw new RuntimeException(e);
            } finally {
              System.out.println("Connection on thread " + Thread.currentThread().getName() + " complete.");
            }
          }, executor));
        }
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).get();
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }
  }

  private static void sendMessage(final String message, final SocketChannel socketChannel) throws IOException {
    final ByteBuffer buffer = ByteBuffer.wrap(message.getBytes(Charset.defaultCharset()));
    while (buffer.hasRemaining()) {
      socketChannel.write(buffer);
    }
  }

  private static void sendMessage(final String message, final OutputStream outputStream) throws IOException {
    outputStream.write(message.getBytes(Charset.defaultCharset()));
    outputStream.flush();
  }

  private static void sendDataNoSerialization() {
    final List<CompletableFuture<?>> futures = new ArrayList<>();
    try (ExecutorService executor = Executors.newFixedThreadPool(THREADS);
        ExecutorService connectionExecutor = Executors.newFixedThreadPool(THREADS)) {
      try (EventLoopGroup workerGroup = new NioEventLoopGroup(THREADS, executor)) {
        final Bootstrap bootstrap = new Bootstrap();
        bootstrap.group(workerGroup)
            .channel(NioSocketChannel.class)
            .option(ChannelOption.SO_KEEPALIVE, true)
            .handler(new NettyClientChannelInitializer());

        try (AutoCloseableIterator<String> iterator = new NoSerializationIterator()) {
          final int partitionSize = Long.valueOf(MAX_RECORDS / THREADS).intValue();
          final Iterator<List<String>> partitions = Iterators.partition(iterator, partitionSize);
          while (partitions.hasNext()) {
            final List<String> partition = partitions.next();
            futures.add(CompletableFuture.runAsync(() -> {
              final ChannelFuture future = bootstrap.connect("localhost", 9090).syncUninterruptibly();
              System.out.println("Connecting to Container Orchestrator on channel " + future.channel().id().asLongText() + "...");
              partition.forEach(message -> future.channel().writeAndFlush(message));
              future.channel().close().syncUninterruptibly();
              System.out.println("Connection on channel " + future.channel().id().asLongText() + " complete.");
            }, connectionExecutor));
          }
          CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).get();
        } catch (final Exception e) {
          throw new RuntimeException(e);
        }
      }
    }
  }

  private static final String FIVE_STRING_COLUMNS_SCHEMA = """
                                                               {
                                                                     "type": "object",
                                                                     "properties": {
                                                                       "field1": {
                                                                         "type": "string"
                                                                       },
                                                                       "field2": {
                                                                         "type": "string"
                                                                       },
                                                                       "field3": {
                                                                         "type": "string"
                                                                       },
                                                                       "field4": {
                                                                         "type": "string"
                                                                       },
                                                                       "field5": {
                                                                         "type": "string"
                                                                       }
                                                                     }
                                                                   }
                                                           """;

  private static final AirbyteCatalog FIVE_STRING_COLUMNS_CATALOG = new AirbyteCatalog().withStreams(List.of(
      new AirbyteStream().withName("stream1").withJsonSchema(Jsons.deserialize(FIVE_STRING_COLUMNS_SCHEMA))
          .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH))));

  @Override
  public AirbyteCatalog discover(JsonNode jsonNode) {
    return FIVE_STRING_COLUMNS_CATALOG;
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(JsonNode jsonNode, ConfiguredAirbyteCatalog configuredAirbyteCatalog, JsonNode jsonNode1) {
    return new DummyIterator();
  }

  public AutoCloseableIterator<String> readNoSerialization() {
    return new NoSerializationIterator();
  }

  public AutoCloseableIterator<AirbyteMessage> read() {
    return new DummyIterator();
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode jsonNode) {
    return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

}
