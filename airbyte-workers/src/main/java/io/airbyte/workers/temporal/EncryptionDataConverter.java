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

package io.airbyte.workers.temporal;

import com.google.common.base.Defaults;
import com.google.protobuf.ByteString;
import io.temporal.api.common.v1.Payload;
import io.temporal.api.common.v1.Payloads;
import io.temporal.common.converter.DataConverter;
import io.temporal.common.converter.DataConverterException;
import java.lang.reflect.Type;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Optional;
import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * EncryptionDataConverter provides the means to encrypt job data stored in Temporal. This is
 * heavily based on
 * https://github.com/temporalio/samples-java/blob/master/src/main/java/io/temporal/samples/encryptedpayloads/CryptDataConverter.java
 * The main difference is that it uses a single key.
 */
public class EncryptionDataConverter implements DataConverter {

  static final String METADATA_ENCODING_KEY = "encoding";
  static final ByteString METADATA_ENCODING =
      ByteString.copyFrom("binary/encrypted", StandardCharsets.UTF_8);

  private static final String CIPHER = "AES/GCM/NoPadding";

  static final String METADATA_ENCRYPTION_CIPHER_KEY = "encryption-cipher";
  static final ByteString METADATA_ENCRYPTION_CIPHER =
      ByteString.copyFrom(CIPHER, StandardCharsets.UTF_8);

  private static final int GCM_NONCE_LENGTH_BYTE = 12;
  private static final int GCM_TAG_LENGTH_BIT = 128;
  private static final Charset UTF_8 = StandardCharsets.UTF_8;

  private final DataConverter converter;
  private final String encryptionKey;

  public EncryptionDataConverter(DataConverter converter, String encryptionKey) {
    this.converter = converter;
    this.encryptionKey = encryptionKey;
  }

  // a nonce is an arbitrary number that can be used just once in a cryptographic communication
  private static byte[] getNonce(int size) {
    byte[] nonce = new byte[size];
    new SecureRandom().nextBytes(nonce);
    return nonce;
  }

  private byte[] encrypt(byte[] plainData, SecretKey key) throws Exception {
    byte[] nonce = getNonce(GCM_NONCE_LENGTH_BYTE);

    Cipher cipher = Cipher.getInstance(CIPHER);
    cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(GCM_TAG_LENGTH_BIT, nonce));

    byte[] encryptedData = cipher.doFinal(plainData);
    return ByteBuffer.allocate(nonce.length + encryptedData.length)
        .put(nonce)
        .put(encryptedData)
        .array();
  }

  private byte[] decrypt(byte[] encryptedDataWithNonce, SecretKey key) throws Exception {
    ByteBuffer buffer = ByteBuffer.wrap(encryptedDataWithNonce);

    byte[] nonce = new byte[GCM_NONCE_LENGTH_BYTE];
    buffer.get(nonce);
    byte[] encryptedData = new byte[buffer.remaining()];
    buffer.get(encryptedData);

    Cipher cipher = Cipher.getInstance(CIPHER);
    cipher.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(GCM_TAG_LENGTH_BIT, nonce));

    return cipher.doFinal(encryptedData);
  }

  @Override
  public <T> Optional<Payload> toPayload(T value) throws DataConverterException {
    return converter.toPayload(value);
  }

  private SecretKey getKey() {
    return new SecretKeySpec(encryptionKey.getBytes(UTF_8), "AES");
  }

  public <T> Optional<Payload> toEncryptedPayload(T value) throws DataConverterException {
    Optional<Payload> optionalPayload = converter.toPayload(value);

    if (optionalPayload.isEmpty()) {
      return optionalPayload;
    }

    Payload innerPayload = optionalPayload.get();

    byte[] encryptedData;
    try {
      encryptedData = encrypt(innerPayload.toByteArray(), getKey());
    } catch (Throwable e) {
      throw new DataConverterException(e);
    }

    Payload encryptedPayload =
        Payload.newBuilder()
            .putMetadata(METADATA_ENCODING_KEY, METADATA_ENCODING)
            .putMetadata(METADATA_ENCRYPTION_CIPHER_KEY, METADATA_ENCRYPTION_CIPHER)
            .setData(ByteString.copyFrom(encryptedData))
            .build();

    return Optional.of(encryptedPayload);
  }

  @Override
  public <T> T fromPayload(Payload payload, Class<T> valueClass, Type valueType) {
    ByteString encoding = payload.getMetadataOrDefault(METADATA_ENCODING_KEY, null);
    if (!encoding.equals(METADATA_ENCODING)) {
      return converter.fromPayload(payload, valueClass, valueType);
    }

    byte[] plainData;
    Payload decryptedPayload;

    try {
      plainData = decrypt(payload.getData().toByteArray(), getKey());
      decryptedPayload = Payload.parseFrom(plainData);
    } catch (Throwable e) {
      throw new DataConverterException(e);
    }

    return converter.fromPayload(decryptedPayload, valueClass, valueType);
  }

  @Override
  public Optional<Payloads> toPayloads(Object... values) throws DataConverterException {
    if (values == null || values.length == 0) {
      return Optional.empty();
    }
    try {
      Payloads.Builder result = Payloads.newBuilder();
      for (Object value : values) {
        Optional<Payload> payload = toEncryptedPayload(value);
        if (payload.isPresent()) {
          result.addPayloads(payload.get());
        } else {
          result.addPayloads(Payload.getDefaultInstance());
        }
      }
      return Optional.of(result.build());
    } catch (DataConverterException e) {
      throw e;
    } catch (Throwable e) {
      throw new DataConverterException(e);
    }
  }

  @Override
  public <T> T fromPayloads(
                            int index,
                            Optional<Payloads> content,
                            Class<T> parameterType,
                            Type genericParameterType)
      throws DataConverterException {
    if (content.isEmpty()) {
      return (T) Defaults.defaultValue((Class<?>) parameterType);
    }
    int count = content.get().getPayloadsCount();
    // To make adding arguments a backwards compatible change
    if (index >= count) {
      return (T) Defaults.defaultValue((Class<?>) parameterType);
    }
    return fromPayload(content.get().getPayloads(index), parameterType, genericParameterType);
  }

}
