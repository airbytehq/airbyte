/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io;

import java.util.Map;
import org.apache.iceberg.PartitionSpec;
import org.apache.iceberg.StructLike;
import org.apache.iceberg.util.StructLikeMap;
import org.apache.iceberg.util.StructLikeUtil;
import org.apache.iceberg.types.Types;

/**
 * Stream-scoped, thread-safe index of identifier values to physical Iceberg row locations.
 *
 * <p>The key is copied when it enters the index because Iceberg record wrappers may be reused.
 */
public final class PositionalDeleteIndex {

  private final Map<StructLike, RowLocation> locations;
  private long maxEntries;

  public PositionalDeleteIndex(Types.StructType keyType) {
    this.locations = StructLikeMap.create(keyType);
  }

  public synchronized RowLocation get(StructLike key) {
    return locations.get(key);
  }

  public synchronized RowLocation remove(StructLike key) {
    return locations.remove(key);
  }

  public synchronized RowLocation replace(StructLike key, RowLocation location) {
    StructLike copiedKey = StructLikeUtil.copy(key);
    RowLocation previous = locations.put(copiedKey, location);
    maxEntries = Math.max(maxEntries, locations.size());
    return previous;
  }

  public synchronized int size() {
    return locations.size();
  }

  public synchronized long maxEntries() {
    return maxEntries;
  }

  public record RowLocation(
      CharSequence path, long position, PartitionSpec spec, StructLike partition) {
    public RowLocation {
      path = path.toString();
      partition = partition == null ? null : StructLikeUtil.copy(partition);
    }
  }

  public record RowLocationMetadata(PartitionSpec spec, StructLike partition) {
    public RowLocationMetadata {
      partition = partition == null ? null : StructLikeUtil.copy(partition);
    }
  }
}
