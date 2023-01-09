/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import java.io.IOException;
import org.apache.iceberg.data.Record;
import org.apache.iceberg.io.CloseableIterable;
import org.apache.iceberg.io.CloseableIterator;

/**
 * @author Leibniz on 2022/11/1.
 */
class EmptyIterator implements CloseableIterable<Record> {

  @Override
  public CloseableIterator<Record> iterator() {
    return new CloseableIterator<Record>() {

      @Override
      public void close() throws IOException {}

      @Override
      public boolean hasNext() {
        return false;
      }

      @Override
      public Record next() {
        return null;
      }

    };
  }

  @Override
  public void close() throws IOException {

  }

}
