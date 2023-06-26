/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.record_buffer.BufferCreateFunction;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.s3.avro.AvroSerializedBuffer;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.io.IOException;
import java.util.concurrent.Callable;
import java.util.function.BiFunction;
import java.util.function.Function;
import org.apache.avro.Schema;
import org.apache.avro.file.CodecFactory;
import org.apache.commons.lang3.StringUtils;

/**
 * This class differs from {@link AvroSerializedBuffer} in that 1) the Avro schema can be customized
 * by the caller, and 2) the message is formatted by {@link BigQueryRecordFormatter}. In this way,
 * this buffer satisfies the needs of both the standard and the denormalized BigQuery destinations.
 */
public class BigQueryAvroSerializedBuffer extends AvroSerializedBuffer {

  private final BigQueryRecordFormatter recordFormatter;

  public BigQueryAvroSerializedBuffer(final BufferStorage bufferStorage,
                                      final CodecFactory codecFactory,
                                      final Schema schema,
                                      final BigQueryRecordFormatter recordFormatter)
      throws Exception {
    super(bufferStorage, codecFactory, schema);
    this.recordFormatter = recordFormatter;
  }

  @Override
  protected void writeRecord(final AirbyteRecordMessage record) throws IOException {
    dataFileWriter.append(avroRecordFactory.getAvroRecord(recordFormatter.formatRecord(record)));
  }

  public static BufferCreateFunction createBufferFunction(final S3AvroFormatConfig config,
                                                          final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator,
                                                          final BiFunction<BigQueryRecordFormatter, AirbyteStreamNameNamespacePair, Schema> schemaCreator,
                                                          final Callable<BufferStorage> createStorageFunction) {
    final CodecFactory codecFactory = config.getCodecFactory();
    return (pair, catalog) -> {
      final AirbyteStream stream = catalog.getStreams()
          .stream()
          .filter(s -> s.getStream().getName().equals(pair.getName()) && StringUtils.equals(s.getStream().getNamespace(), pair.getNamespace()))
          .findFirst()
          .orElseThrow(() -> new RuntimeException(String.format("No such stream %s.%s", pair.getNamespace(), pair.getName())))
          .getStream();
      final BigQueryRecordFormatter recordFormatter = recordFormatterCreator.apply(stream.getJsonSchema());
      final Schema schema = schemaCreator.apply(recordFormatter, pair);
      return new BigQueryAvroSerializedBuffer(createStorageFunction.call(), codecFactory, schema, recordFormatter);
    };
  }

}
