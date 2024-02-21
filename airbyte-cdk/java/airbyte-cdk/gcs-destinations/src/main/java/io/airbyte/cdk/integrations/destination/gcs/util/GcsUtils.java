/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.gcs.util;

import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants;
import javax.annotation.Nullable;
import org.apache.avro.LogicalTypes;
import org.apache.avro.Schema;
import org.apache.avro.SchemaBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsUtils.class);
  private static final Schema UUID_SCHEMA = LogicalTypes.uuid().addToSchema(Schema.create(Schema.Type.STRING));
  private static final Schema TIMESTAMP_MILLIS_SCHEMA = LogicalTypes.timestampMillis().addToSchema(Schema.create(Schema.Type.LONG));
  private static final Schema NULLABLE_TIMESTAMP_MILLIS = SchemaBuilder.builder().unionOf().nullType().and().type(TIMESTAMP_MILLIS_SCHEMA).endUnion();

  public static Schema getDefaultAvroSchema(final String name,
                                            @Nullable final String namespace,
                                            final boolean appendAirbyteFields,
                                            final boolean useDestinationsV2Columns) {
    LOGGER.info("Default schema.");
    final String stdName = AvroConstants.NAME_TRANSFORMER.getIdentifier(name);
    final String stdNamespace = AvroConstants.NAME_TRANSFORMER.getNamespace(namespace);
    SchemaBuilder.RecordBuilder<Schema> builder = SchemaBuilder.record(stdName);

    if (stdNamespace != null) {
      builder = builder.namespace(stdNamespace);
    }
    if (useDestinationsV2Columns) {
      builder.namespace("airbyte");
    }

    SchemaBuilder.FieldAssembler<Schema> assembler = builder.fields();
    if (useDestinationsV2Columns) {
      if (appendAirbyteFields) {
        assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID).type(UUID_SCHEMA).noDefault();
        assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT).type(TIMESTAMP_MILLIS_SCHEMA).noDefault();
        assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT).type(NULLABLE_TIMESTAMP_MILLIS).withDefault(null);
      }
    } else {
      if (appendAirbyteFields) {
        assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_ID).type(UUID_SCHEMA).noDefault();
        assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).type(TIMESTAMP_MILLIS_SCHEMA).noDefault();
      }
    }
    assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_DATA).type().stringType().noDefault();

    return assembler.endRecord();
  }

}
