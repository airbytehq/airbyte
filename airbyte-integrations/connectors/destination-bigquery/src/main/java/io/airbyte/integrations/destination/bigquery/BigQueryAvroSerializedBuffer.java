package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.avro.AvroSerializedBuffer;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.concurrent.Callable;
import java.util.function.Function;
import org.apache.avro.Schema;
import org.apache.avro.file.CodecFactory;
import org.apache.commons.lang3.StringUtils;

public class BigQueryAvroSerializedBuffer extends AvroSerializedBuffer {

  private final BigQueryRecordFormatter recordFormatter;

  public BigQueryAvroSerializedBuffer(final BufferStorage bufferStorage,
                                      final CodecFactory codecFactory,
                                      final Schema schema,
                                      final BigQueryRecordFormatter recordFormatter) throws Exception {
    super(bufferStorage, codecFactory, schema);
    this.recordFormatter = recordFormatter;
  }

  @Override
  protected void writeRecord(final AirbyteRecordMessage recordMessage) throws IOException {
    dataFileWriter.append(avroRecordFactory.getAvroRecord(recordFormatter.formatRecord(recordMessage)));
  }

  public static CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> createFunction(final S3AvroFormatConfig config,
                                                                                                                                          final Function<AirbyteStream, Schema> schemaCreator,
                                                                                                                                          final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator,
                                                                                                                                          final Callable<BufferStorage> createStorageFunction) {
    final CodecFactory codecFactory = config.getCodecFactory();
    return (pair, catalog) -> {
      final AirbyteStream stream = catalog.getStreams()
          .stream()
          .filter(s -> s.getStream().getName().equals(pair.getName()) && StringUtils.equals(s.getStream().getNamespace(), pair.getNamespace()))
          .findFirst()
          .orElseThrow(() -> new RuntimeException(String.format("No such stream %s.%s", pair.getNamespace(), pair.getName())))
          .getStream();
      return new BigQueryAvroSerializedBuffer(createStorageFunction.call(), codecFactory, schemaCreator.apply(stream), recordFormatterCreator.apply(stream.getJsonSchema()));
    };
  }

}
