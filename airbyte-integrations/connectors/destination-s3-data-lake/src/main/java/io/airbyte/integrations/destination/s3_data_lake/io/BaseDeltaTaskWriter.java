/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io;

import java.io.IOException;
import java.util.Set;
import org.apache.iceberg.FileFormat;
import org.apache.iceberg.PartitionKey;
import org.apache.iceberg.PartitionSpec;
import org.apache.iceberg.Schema;
import org.apache.iceberg.StructLike;
import org.apache.iceberg.data.GenericRecord;
import org.apache.iceberg.data.InternalRecordWrapper;
import org.apache.iceberg.data.Record;
import org.apache.iceberg.io.BaseTaskWriter;
import org.apache.iceberg.io.FileAppenderFactory;
import org.apache.iceberg.io.FileIO;
import org.apache.iceberg.io.OutputFileFactory;
import org.apache.iceberg.types.TypeUtil;
import org.apache.iceberg.types.Types;

/**
 * Implementation of the Iceberg {@link BaseTaskWriter} that handles delta-based updates (insert,
 * update, delete).
 * <p />
 * <b>N.B.</b>: This class is implemented in Java due to visibility of the
 * {@link BaseEqualityDeltaWriter}. That class is marked as {@code protected}, which is less visible
 * than the {@link BaseTaskWriter} class or any other subclasses. This is not allowed in Kotlin, so
 * this class is implemented in Java where that it is allowed. This class should not be converted to
 * Kotlin while the visibility is still lesser in the super class.
 */
public abstract class BaseDeltaTaskWriter extends BaseTaskWriter<Record> {

  private final Schema schema;
  private final Schema deleteSchema;
  private final InternalRecordWrapper wrapper;
  private final InternalRecordWrapper keyWrapper;

  public BaseDeltaTaskWriter(final PartitionSpec spec,
                             final FileFormat format,
                             final FileAppenderFactory<Record> appenderFactory,
                             final OutputFileFactory fileFactory,
                             final FileIO io,
                             final long targetFileSize,
                             final Schema schema,
                             final Set<Integer> identifierFieldIds) {
    super(spec, format, appenderFactory, fileFactory, io, targetFileSize);
    this.schema = schema;
    this.deleteSchema = TypeUtil.select(schema, identifierFieldIds);
    this.wrapper = new InternalRecordWrapper(schema.asStruct());
    this.keyWrapper = new InternalRecordWrapper(deleteSchema.asStruct());
  }

  public abstract RowDataDeltaWriter route(final Record row);

  public InternalRecordWrapper wrapper() {
    return wrapper;
  }

  private Record constructIdentifierRecord(Record row) {
    final GenericRecord recordWithIds = GenericRecord.create(deleteSchema);

    for (final Types.NestedField idField : deleteSchema.columns()) {
      recordWithIds.setField(idField.name(), row.getField(idField.name()));
    }

    return recordWithIds;
  }

  @Override
  public void write(final Record row) throws IOException {
    final RowDataDeltaWriter writer = route(row);
    final Operation rowOperation = getOperation(row);
    if (rowOperation == Operation.INSERT) {
      writer.write(row);
    } else if (rowOperation == Operation.DELETE) {
      writer.deleteKey(constructIdentifierRecord(row));
    } else {
      writer.deleteKey(constructIdentifierRecord(row));
      writer.write(row);
    }
  }

  private Operation getOperation(final Record row) {
    if (row instanceof RecordWrapper) {
      return ((RecordWrapper) row).getOperation();
    } else {
      return Operation.INSERT;
    }
  }

  /**
   * Custom writer implementation that supports inserting and deleting records based on equality.
   */
  public class RowDataDeltaWriter extends BaseEqualityDeltaWriter {

    public RowDataDeltaWriter(final PartitionKey partition) {
      super(partition, schema, deleteSchema);
    }

    @Override
    protected StructLike asStructLike(final Record data) {
      return wrapper.wrap(data);
    }

    @Override
    protected StructLike asStructLikeKey(final Record data) {
      return keyWrapper.wrap(data);
    }

  }

}
