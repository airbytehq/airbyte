/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import java.io.EOFException;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.apache.kafka.connect.errors.ConnectException;
import org.apache.kafka.connect.util.SafeObjectInputStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class handles reading and writing a debezium offset file. In many cases it is duplicating
 * logic in debezium because that logic is not exposed in the public API. We mostly treat the
 * contents of this state file like a black box. We know it is a Map<ByteBuffer, Bytebuffer>. We
 * deserialize it to a Map<String, String> so that the state file can be human readable. If we ever
 * discover that any of the contents of these offset files is not string serializable we will likely
 * have to drop the human readability support and just base64 encode it.
 */
public class AirbyteFileOffsetBackingStore {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteFileOffsetBackingStore.class);

  private final Path offsetFilePath;

  public AirbyteFileOffsetBackingStore(final Path offsetFilePath) {
    this.offsetFilePath = offsetFilePath;
  }

  public Path getOffsetFilePath() {
    return offsetFilePath;
  }

  public Map<String, String> read() {
    final Map<ByteBuffer, ByteBuffer> raw = load();

    return raw.entrySet().stream().collect(Collectors.toMap(
        e -> byteBufferToString(e.getKey()),
        e -> byteBufferToString(e.getValue())));
  }

  @SuppressWarnings("unchecked")
  public void persist(JsonNode cdcState) {
    final Map<String, String> mapAsString =
        cdcState != null ? Jsons.object(cdcState, Map.class) : Collections.emptyMap();
    final Map<ByteBuffer, ByteBuffer> mappedAsStrings = mapAsString.entrySet().stream().collect(Collectors.toMap(
        e -> stringToByteBuffer(e.getKey()),
        e -> stringToByteBuffer(e.getValue())));

    FileUtils.deleteQuietly(offsetFilePath.toFile());
    save(mappedAsStrings);
  }

  private static String byteBufferToString(ByteBuffer byteBuffer) {
    Preconditions.checkNotNull(byteBuffer);
    return new String(byteBuffer.array(), StandardCharsets.UTF_8);
  }

  private static ByteBuffer stringToByteBuffer(String s) {
    Preconditions.checkNotNull(s);
    return ByteBuffer.wrap(s.getBytes(StandardCharsets.UTF_8));
  }

  /**
   * See FileOffsetBackingStore#load - logic is mostly borrowed from here. duplicated because this
   * method is not public.
   */
  @SuppressWarnings("unchecked")
  private Map<ByteBuffer, ByteBuffer> load() {
    try (final SafeObjectInputStream is = new SafeObjectInputStream(Files.newInputStream(offsetFilePath))) {
      final Object obj = is.readObject();
      if (!(obj instanceof HashMap))
        throw new ConnectException("Expected HashMap but found " + obj.getClass());
      final Map<byte[], byte[]> raw = (Map<byte[], byte[]>) obj;
      final Map<ByteBuffer, ByteBuffer> data = new HashMap<>();
      for (Map.Entry<byte[], byte[]> mapEntry : raw.entrySet()) {
        final ByteBuffer key = (mapEntry.getKey() != null) ? ByteBuffer.wrap(mapEntry.getKey()) : null;
        final ByteBuffer value = (mapEntry.getValue() != null) ? ByteBuffer.wrap(mapEntry.getValue()) : null;
        data.put(key, value);
      }

      return data;
    } catch (NoSuchFileException | EOFException e) {
      // NoSuchFileException: Ignore, may be new.
      // EOFException: Ignore, this means the file was missing or corrupt
      return Collections.emptyMap();
    } catch (IOException | ClassNotFoundException e) {
      throw new ConnectException(e);
    }
  }

  /**
   * See FileOffsetBackingStore#save - logic is mostly borrowed from here. duplicated because this
   * method is not public.
   */
  private void save(Map<ByteBuffer, ByteBuffer> data) {
    try (ObjectOutputStream os = new ObjectOutputStream(Files.newOutputStream(offsetFilePath))) {
      Map<byte[], byte[]> raw = new HashMap<>();
      for (Map.Entry<ByteBuffer, ByteBuffer> mapEntry : data.entrySet()) {
        byte[] key = (mapEntry.getKey() != null) ? mapEntry.getKey().array() : null;
        byte[] value = (mapEntry.getValue() != null) ? mapEntry.getValue().array() : null;
        raw.put(key, value);
      }
      os.writeObject(raw);
    } catch (IOException e) {
      throw new ConnectException(e);
    }
  }

  public static AirbyteFileOffsetBackingStore initializeState(JsonNode cdcState) {
    final Path cdcWorkingDir;
    try {
      cdcWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-state-offset");
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    final Path cdcOffsetFilePath = cdcWorkingDir.resolve("offset.dat");

    final AirbyteFileOffsetBackingStore offsetManager = new AirbyteFileOffsetBackingStore(cdcOffsetFilePath);
    offsetManager.persist(cdcState);
    return offsetManager;
  }

}
