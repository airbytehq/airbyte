/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.BiFunction;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.apache.kafka.connect.errors.ConnectException;
import org.apache.kafka.connect.util.SafeObjectInputStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class handles reading and writing a debezium offset file. In many cases it is duplicating
 * logic in debezium because that logic is not exposed in the public API. We mostly treat the
 * contents of this state file like a black box. We know it is a Map&lt;ByteBuffer, Bytebuffer&gt;.
 * We deserialize it to a Map&lt;String, String&gt; so that the state file can be human readable. If
 * we ever discover that any of the contents of these offset files is not string serializable we
 * will likely have to drop the human readability support and just base64 encode it.
 */
public class AirbyteFileOffsetBackingStore {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteFileOffsetBackingStore.class);
  private static final BiFunction<String, String, String> SQL_SERVER_STATE_MUTATION = (key, databaseName) -> key.substring(0, key.length() - 2)
      + ",\"database\":\"" + databaseName + "\"" + key.substring(key.length() - 2);
  private final Path offsetFilePath;
  private final Optional<String> dbName;

  public AirbyteFileOffsetBackingStore(final Path offsetFilePath, final Optional<String> dbName) {
    this.offsetFilePath = offsetFilePath;
    this.dbName = dbName;
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
  public void persist(final JsonNode cdcState) {
    final Map<String, String> mapAsString =
        cdcState != null ? Jsons.object(cdcState, Map.class) : Collections.emptyMap();

    final Map<String, String> updatedMap = updateStateForDebezium2_1(mapAsString);

    final Map<ByteBuffer, ByteBuffer> mappedAsStrings = updatedMap.entrySet().stream().collect(Collectors.toMap(
        e -> stringToByteBuffer(e.getKey()),
        e -> stringToByteBuffer(e.getValue())));

    FileUtils.deleteQuietly(offsetFilePath.toFile());
    save(mappedAsStrings);
  }

  private Map<String, String> updateStateForDebezium2_1(final Map<String, String> mapAsString) {
    final Map<String, String> updatedMap = new LinkedHashMap<>();
    if (mapAsString.size() > 0) {
      final String key = mapAsString.keySet().stream().toList().get(0);
      final int i = key.indexOf('[');
      final int i1 = key.lastIndexOf(']');

      if (i == 0 && i1 == key.length() - 1) {
        // The state is Debezium 2.1 compatible. No need to change anything.
        return mapAsString;
      }

      LOGGER.info("Mutating sate to make it Debezium 2.1 compatible");
      final String newKey = dbName.isPresent() ? SQL_SERVER_STATE_MUTATION.apply(key.substring(i, i1 + 1), dbName.get()) : key.substring(i, i1 + 1);
      final String value = mapAsString.get(key);
      updatedMap.put(newKey, value);
    }
    return updatedMap;
  }

  private static String byteBufferToString(final ByteBuffer byteBuffer) {
    Preconditions.checkNotNull(byteBuffer);
    return new String(byteBuffer.array(), StandardCharsets.UTF_8);
  }

  private static ByteBuffer stringToByteBuffer(final String s) {
    Preconditions.checkNotNull(s);
    return ByteBuffer.wrap(s.getBytes(StandardCharsets.UTF_8));
  }

  /**
   * See FileOffsetBackingStore#load - logic is mostly borrowed from here. duplicated because this
   * method is not public. Reduced the try catch block to only the read operation from original code
   * to reduce errors when reading the file.
   */
  @SuppressWarnings("unchecked")
  private Map<ByteBuffer, ByteBuffer> load() {
    Object obj;
    try (final SafeObjectInputStream is = new SafeObjectInputStream(Files.newInputStream(offsetFilePath))) {
      // todo (cgardens) - we currently suppress a security warning for this line. use of readObject from
      // untrusted sources is considered unsafe. Since the source is controlled by us in this case it
      // should be safe. That said, changing this implementation to not use readObject would remove some
      // headache.
      obj = is.readObject();
    } catch (final NoSuchFileException | EOFException e) {
      // NoSuchFileException: Ignore, may be new.
      // EOFException: Ignore, this means the file was missing or corrupt
      return Collections.emptyMap();
    } catch (final IOException | ClassNotFoundException e) {
      throw new ConnectException(e);
    }

    if (!(obj instanceof HashMap))
      throw new ConnectException("Expected HashMap but found " + obj.getClass());
    final Map<byte[], byte[]> raw = (Map<byte[], byte[]>) obj;
    final Map<ByteBuffer, ByteBuffer> data = new HashMap<>();
    for (final Map.Entry<byte[], byte[]> mapEntry : raw.entrySet()) {
      final ByteBuffer key = (mapEntry.getKey() != null) ? ByteBuffer.wrap(mapEntry.getKey()) : null;
      final ByteBuffer value = (mapEntry.getValue() != null) ? ByteBuffer.wrap(mapEntry.getValue()) : null;
      data.put(key, value);
    }

    return data;
  }

  /**
   * See FileOffsetBackingStore#save - logic is mostly borrowed from here. duplicated because this
   * method is not public.
   */
  private void save(final Map<ByteBuffer, ByteBuffer> data) {
    try (final ObjectOutputStream os = new ObjectOutputStream(Files.newOutputStream(offsetFilePath))) {
      final Map<byte[], byte[]> raw = new HashMap<>();
      for (final Map.Entry<ByteBuffer, ByteBuffer> mapEntry : data.entrySet()) {
        final byte[] key = (mapEntry.getKey() != null) ? mapEntry.getKey().array() : null;
        final byte[] value = (mapEntry.getValue() != null) ? mapEntry.getValue().array() : null;
        raw.put(key, value);
      }
      os.writeObject(raw);
    } catch (final IOException e) {
      throw new ConnectException(e);
    }
  }

  public static AirbyteFileOffsetBackingStore initializeState(final JsonNode cdcState, final Optional<String> dbName) {
    final Path cdcWorkingDir;
    try {
      cdcWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-state-offset");
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    final Path cdcOffsetFilePath = cdcWorkingDir.resolve("offset.dat");

    final AirbyteFileOffsetBackingStore offsetManager = new AirbyteFileOffsetBackingStore(cdcOffsetFilePath, dbName);
    offsetManager.persist(cdcState);
    return offsetManager;
  }

  public static AirbyteFileOffsetBackingStore initializeDummyStateForSnapshotPurpose() {
    final Path cdcWorkingDir;
    try {
      cdcWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-dummy-state-offset");
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    final Path cdcOffsetFilePath = cdcWorkingDir.resolve("offset.dat");

    return new AirbyteFileOffsetBackingStore(cdcOffsetFilePath, Optional.empty());
  }

}
