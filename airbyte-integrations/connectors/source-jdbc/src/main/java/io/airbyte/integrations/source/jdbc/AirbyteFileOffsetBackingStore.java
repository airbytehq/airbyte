/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.jdbc.models.CdcState;
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
import org.apache.kafka.connect.storage.FileOffsetBackingStore;
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

  public static final Path DEFAULT_OFFSET_STORAGE_PATH = Path.of("/tmp/offset.dat");

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteFileOffsetBackingStore.class);

  private final Path offsetFilePath;

  public AirbyteFileOffsetBackingStore() {
    this(DEFAULT_OFFSET_STORAGE_PATH);
  }

  @VisibleForTesting
  AirbyteFileOffsetBackingStore(final Path offsetFilePath) {
    this.offsetFilePath = offsetFilePath;
  }

  public CdcState read() {
    final Map<ByteBuffer, ByteBuffer> raw = load();

    final Map<String, String> mappedAsStrings = raw.entrySet().stream().collect(Collectors.toMap(
        e -> e.getKey() != null ? new String(e.getKey().array(), StandardCharsets.UTF_8) : null,
        e -> e.getValue() != null ? new String(e.getValue().array(), StandardCharsets.UTF_8) : null));
    final JsonNode asJson = Jsons.jsonNode(mappedAsStrings);

    LOGGER.info("debezium state. {}", asJson);

    return new CdcState().withState(asJson);
  }

  @SuppressWarnings("unchecked")
  public void persist(CdcState cdcState) {
    final Map<String, String> mapAsString =
        cdcState != null && cdcState.getState() != null ? Jsons.object(cdcState.getState(), Map.class) : Collections.emptyMap();
    final Map<ByteBuffer, ByteBuffer> mappedAsStrings = mapAsString.entrySet().stream().collect(Collectors.toMap(
        e -> e.getKey() != null ? ByteBuffer.wrap(e.getKey().getBytes(StandardCharsets.UTF_8)) : null,
        e -> e.getValue() != null ? ByteBuffer.wrap(e.getValue().getBytes(StandardCharsets.UTF_8)) : null));

    FileUtils.deleteQuietly(DEFAULT_OFFSET_STORAGE_PATH.toFile());
    save(mappedAsStrings);
  }

  /**
   * See {@link FileOffsetBackingStore#load} - logic is mostly borrowed from here. duplicated because
   * this method is not public.
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
   * See {@link FileOffsetBackingStore#save} - logic is mostly borrowed from here. duplicated because
   * this method is not public.
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

}
