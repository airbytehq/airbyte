/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io;

import io.airbyte.cdk.ConfigErrorException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
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
import org.apache.iceberg.deletes.PositionDelete;
import org.apache.iceberg.deletes.PositionDeleteWriter;
import org.apache.iceberg.io.BaseTaskWriter;
import org.apache.iceberg.io.DeleteWriteResult;
import org.apache.iceberg.io.FileIO;
import org.apache.iceberg.io.OutputFileFactory;
import org.apache.iceberg.io.WriteResult;
import org.apache.iceberg.types.TypeUtil;
import org.apache.iceberg.types.Types;

/**
 * Delta writer that emits only positional deletes.
 *
 * <p>
 * The location index is shared by every aggregate for one stream. This mirrors the location
 * tracking in Iceberg's BaseEqualityDeltaWriter while making it available across writer instances.
 */
public abstract class BasePositionDeltaTaskWriter extends BaseTaskWriter<Record> {

  private final Table table;
  private final Schema deleteSchema;
  private final InternalRecordWrapper wrapper;
  private final InternalRecordWrapper keyWrapper;
  private final PositionalDeleteIndex index;
  private final GenericFileWriterFactory writerFactory;
  private final OutputFileFactory fileFactory;
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
                                        final PositionalDeleteIndex index) {
    super(spec, format, writerFactory, fileFactory, io, targetFileSize);
    this.table = table;
    this.deleteSchema = TypeUtil.select(schema, identifierFieldIds);
    this.wrapper = new InternalRecordWrapper(schema.asStruct());
    this.keyWrapper = new InternalRecordWrapper(deleteSchema.asStruct());
    this.index = index;
    this.writerFactory = writerFactory;
    this.fileFactory = fileFactory;
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
    RowDataPositionDeltaWriter writer = route(row);
    Operation rowOperation = getOperation(row);
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
    }
    return Operation.INSERT;
  }

  @Override
  public WriteResult complete() throws IOException {
    close();
    WriteResult dataResult = super.complete();
    WriteResult.Builder result = WriteResult.builder().addDataFiles(dataResult.dataFiles());
    result.addDeleteFiles(dataResult.deleteFiles());
    synchronized (completedPositionDeleteFiles) {
      result.addDeleteFiles(completedPositionDeleteFiles);
    }
    return result.build();
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
    private final Map<BucketKey, PositionDeleteWriterState> positionDeleteWriters = new HashMap<>();
    private final RollingFileWriter dataWriter;
    private boolean closed;

    public RowDataPositionDeltaWriter(StructLike partition) {
      this.partition = partition;
      this.dataWriter = new RollingFileWriter(partition);
    }

    public void write(Record row) throws IOException {
      StructLike key = keyWrapper.wrap(constructIdentifierRecord(row));
      PositionalDeleteIndex.RowLocation location =
          new PositionalDeleteIndex.RowLocation(
              dataWriter.currentPath(), dataWriter.currentRows(), spec(), partition);
      PositionalDeleteIndex.RowLocation previous = index.replace(key, location);
      if (previous != null) {
        writePositionDelete(previous);
      }
      dataWriter.write(row);
    }

    public void deleteKey(Record keyRecord) {
      PositionalDeleteIndex.RowLocation previous = index.remove(keyWrapper.wrap(keyRecord));
      if (previous != null) {
        writePositionDelete(previous);
      }
    }

    private void writePositionDelete(PositionalDeleteIndex.RowLocation location) {
      BucketKey key = new BucketKey(location.spec(), location.partition());
      PositionDeleteWriterState state =
          positionDeleteWriters.computeIfAbsent(
              key, ignored -> new PositionDeleteWriterState(location.spec(), location.partition()));
      state.locations.add(location);
    }

    @Override
    public void close() throws IOException {
      if (!closed) {
        try {
          dataWriter.close();
          for (PositionDeleteWriterState state : positionDeleteWriters.values()) {
            state.writeSorted();
          }
        } finally {
          closed = true;
        }
      }
    }

    private record BucketKey(PartitionSpec spec, StructLike partition) {

      @Override
      public boolean equals(Object other) {
        if (!(other instanceof BucketKey that) || !spec.equals(that.spec)) {
          return false;
        }
        if (partition == that.partition) {
          return true;
        }
        if (partition == null || that.partition == null || partition.size() != that.partition.size()) {
          return false;
        }
        for (int i = 0; i < partition.size(); i++) {
          if (!Objects.equals(partition.get(i, Object.class), that.partition.get(i, Object.class))) {
            return false;
          }
        }
        return true;
      }

      @Override
      public int hashCode() {
        int result = spec.hashCode();
        if (partition != null) {
          for (int i = 0; i < partition.size(); i++) {
            result = 31 * result + Objects.hashCode(partition.get(i, Object.class));
          }
        }
        return result;
      }

    }

    private final class PositionDeleteWriterState {

      private final PartitionSpec spec;
      private final StructLike partition;
      private final List<PositionalDeleteIndex.RowLocation> locations = new ArrayList<>();

      private PositionDeleteWriterState(PartitionSpec spec, StructLike partition) {
        this.spec = spec;
        this.partition = partition;
      }

      private void writeSorted() throws IOException {
        if (locations.isEmpty()) {
          return;
        }
        locations.sort(
            Comparator.comparing((PositionalDeleteIndex.RowLocation location) -> location.path().toString())
                .thenComparingLong(PositionalDeleteIndex.RowLocation::position));
        PositionDeleteWriter<Record> writer =
            writerFactory.newPositionDeleteWriter(
                fileFactory.newOutputFile(spec, partition), spec, partition);
        try {
          for (PositionalDeleteIndex.RowLocation location : locations) {
            PositionDelete<Record> positionDelete = PositionDelete.create();
            positionDelete.set(location.path(), location.position());
            writer.write(positionDelete);
          }
        } finally {
          writer.close();
        }
        DeleteWriteResult result = writer.result();
        result.deleteFiles().forEach(BasePositionDeltaTaskWriter.this::addCompletedPositionDeleteFile);
      }

    }

  }

  protected PositionalDeleteIndex index() {
    return index;
  }

}
