/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io;

import io.airbyte.cdk.ConfigErrorException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import org.apache.iceberg.DataFile;
import org.apache.iceberg.DeleteFile;
import org.apache.iceberg.FileFormat;
import org.apache.iceberg.PartitionSpec;
import org.apache.iceberg.Schema;
import org.apache.iceberg.StructLike;
import org.apache.iceberg.Table;
import org.apache.iceberg.data.GenericFileWriterFactory;
import org.apache.iceberg.data.GenericRecord;
import org.apache.iceberg.data.InternalRecordWrapper;
import org.apache.iceberg.data.Record;
import org.apache.iceberg.io.BaseTaskWriter;
import org.apache.iceberg.io.FileIO;
import org.apache.iceberg.io.OutputFileFactory;
import org.apache.iceberg.io.WriteResult;
import org.apache.iceberg.types.TypeUtil;
import org.apache.iceberg.types.Types;

/**
 * Delta writer that emits only positional deletes.
 */
public abstract class BasePositionDeltaTaskWriter extends BaseTaskWriter<Record> {

  private final Table table;
  private final Schema deleteSchema;
  private final InternalRecordWrapper wrapper;
  private final InternalRecordWrapper keyWrapper;
  private final PositionalDeleteResolver resolver;
  private final TouchedKeys touchedKeys;
  private final Set<DataFile> fullySupersededDataFiles = new HashSet<>();
  private final List<DeleteFile> completedPositionDeleteFiles = new ArrayList<>();

  protected BasePositionDeltaTaskWriter(
                                        final Table table,
                                        final PartitionSpec spec,
                                        final FileFormat format,
                                        final GenericFileWriterFactory writerFactory,
                                        final OutputFileFactory fileFactory,
                                        final FileIO io,
                                        final long targetFileSize,
                                        final Schema schema,
                                        final Set<Integer> identifierFieldIds,
                                        final PositionalDeleteResolver resolver) {
    super(spec, format, writerFactory, fileFactory, io, targetFileSize);
    this.table = table;
    this.deleteSchema = TypeUtil.select(schema, identifierFieldIds);
    this.wrapper = new InternalRecordWrapper(schema.asStruct());
    this.keyWrapper = new InternalRecordWrapper(deleteSchema.asStruct());
    this.resolver = resolver;
    this.touchedKeys = new TouchedKeys(deleteSchema.asStruct(), resolver.maxTouchedKeys());
  }

  public abstract RowDataPositionDeltaWriter route(Record row);

  protected InternalRecordWrapper wrapper() {
    return wrapper;
  }

  private Record constructIdentifierRecord(Record row) {
    final GenericRecord recordWithIds = GenericRecord.create(deleteSchema);
    for (Types.NestedField idField : deleteSchema.columns()) {
      Object value = row.getField(idField.name());
      if (value == null) {
        throw new ConfigErrorException(
            "Error in stream " + table.name() + ": " + BaseDeltaTaskWriter.NULL_PK_ERROR_MESSAGE,
            null);
      }
      recordWithIds.setField(
          idField.name(), value instanceof CharSequence ? value.toString() : value);
    }
    return recordWithIds;
  }

  @Override
  public void write(final Record row) throws IOException {
    Record identifierRecord = constructIdentifierRecord(row);
    StructLike key = keyWrapper.wrap(identifierRecord);
    RowDataPositionDeltaWriter writer = route(row);
    Operation rowOperation = getOperation(row);
    if (rowOperation == Operation.INSERT) {
      touchedKeys.markInserted(key, writer.writeAndGetLocation(row));
    } else if (rowOperation == Operation.DELETE) {
      touchedKeys.markDeleted(key);
    } else {
      touchedKeys.markDeleted(key);
      touchedKeys.markWritten(key, writer.writeAndGetLocation(row));
    }
    if (touchedKeys.isFull()) {
      resolvePending();
    }
  }

  private Operation getOperation(final Record row) {
    if (row instanceof RecordWrapper) {
      return ((RecordWrapper) row).getOperation();
    }
    return Operation.INSERT;
  }

  @Override
  public WriteResult complete() throws IOException {
    close();
    resolvePending();
    WriteResult dataResult = super.complete();
    WriteResult.Builder result = WriteResult.builder().addDataFiles(dataResult.dataFiles());
    result.addDeleteFiles(dataResult.deleteFiles());
    result.addReferencedDataFiles(dataResult.referencedDataFiles());
    synchronized (completedPositionDeleteFiles) {
      result.addDeleteFiles(completedPositionDeleteFiles);
      completedPositionDeleteFiles.stream()
          .map(DeleteFile::referencedDataFile)
          .filter(Objects::nonNull)
          .forEach(result::addReferencedDataFiles);
    }
    fullySupersededDataFiles.stream()
        .map(dataFile -> dataFile.location())
        .forEach(result::addReferencedDataFiles);
    return result.build();
  }

  private void resolvePending() {
    if (touchedKeys.isEmpty()) {
      return;
    }
    List<DeleteFile> resolved = resolver.resolve(touchedKeys);
    fullySupersededDataFiles.addAll(resolver.fullySupersededDataFiles());
    resolved.forEach(this::addCompletedPositionDeleteFile);
    touchedKeys.clear();
  }

  private void addCompletedPositionDeleteFile(DeleteFile deleteFile) {
    if (deleteFile != null) {
      synchronized (completedPositionDeleteFiles) {
        completedPositionDeleteFiles.add(deleteFile);
      }
    }
  }

  public class RowDataPositionDeltaWriter implements AutoCloseable {

    private final StructLike partition;
    private final RollingFileWriter dataWriter;
    private boolean closed;

    public RowDataPositionDeltaWriter(StructLike partition) {
      this.partition = partition;
      this.dataWriter = new RollingFileWriter(partition);
    }

    public PositionalDeleteResolver.RowLocation writeAndGetLocation(Record row) throws IOException {
      PositionalDeleteResolver.RowLocation location =
          new PositionalDeleteResolver.RowLocation(
              dataWriter.currentPath(), dataWriter.currentRows(), spec(), partition);
      dataWriter.write(row);
      return location;
    }

    @Override
    public void close() throws IOException {
      if (!closed) {
        try {
          dataWriter.close();
        } finally {
          closed = true;
        }
      }
    }

  }

}
