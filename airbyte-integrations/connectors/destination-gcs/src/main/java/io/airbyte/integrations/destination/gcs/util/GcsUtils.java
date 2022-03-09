/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.util;

import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import javax.annotation.Nullable;
import org.apache.avro.LogicalTypes;
import org.apache.avro.Schema;
import org.apache.avro.SchemaBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsUtils.class);

  public static Schema getDefaultAvroSchema(final String name,
                                            @Nullable final String namespace,
                                            final boolean appendAirbyteFields) {
    LOGGER.info("Default schema.");
    final String stdName = AvroConstants.NAME_TRANSFORMER.getIdentifier(name);
    SchemaBuilder.RecordBuilder<Schema> builder = SchemaBuilder.record(stdName);

    if (namespace != null) {
      builder = builder.namespace(namespace);
    }

    SchemaBuilder.FieldAssembler<Schema> assembler = builder.fields();

    Schema TIMESTAMP_MILLIS_SCHEMA = LogicalTypes.timestampMillis()
        .addToSchema(Schema.create(Schema.Type.LONG));
    Schema UUID_SCHEMA = LogicalTypes.uuid()
        .addToSchema(Schema.create(Schema.Type.STRING));

    if (appendAirbyteFields) {
      assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_ID).type(UUID_SCHEMA).noDefault();
      assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
          .type(TIMESTAMP_MILLIS_SCHEMA).noDefault();
    }
    assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_DATA).type().stringType().noDefault();

    return assembler.endRecord();
  }

}
