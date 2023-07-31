/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.util.Optional;
import java.util.function.Supplier;

/**
 * A {@link AutoCloseableIterator} that calls the provided supplier the first time
 * {@link AutoCloseableIterator#hasNext} or {@link AutoCloseableIterator#next} is called. If
 * {@link AutoCloseableIterator#hasNext} or {@link AutoCloseableIterator#next} are never called,
 * then the supplier will never be called. This means if the iterator is closed in this state, the
 * close function on the input iterator will not be called. The assumption here is that if nothing
 * is ever supplied, then there is nothing to close.
 *
 * @param <T> type
 */
class LazyAutoCloseableIterator<T> extends AbstractIterator<T> implements AutoCloseableIterator<T>, AirbyteStreamAware {

  private final Supplier<AutoCloseableIterator<T>> iteratorSupplier;

  private final AirbyteStreamNameNamespacePair airbyteStream;
  private boolean hasSupplied;
  private AutoCloseableIterator<T> internalIterator;

  public LazyAutoCloseableIterator(final Supplier<AutoCloseableIterator<T>> iteratorSupplier, final AirbyteStreamNameNamespacePair airbyteStream) {
    Preconditions.checkNotNull(iteratorSupplier);
    this.airbyteStream = airbyteStream;
    this.iteratorSupplier = iteratorSupplier;
    this.hasSupplied = false;
  }

  @Override
  protected T computeNext() {
    if (!hasSupplied) {
      internalIterator = iteratorSupplier.get();
      Preconditions.checkNotNull(internalIterator, "Supplied iterator was null.");
      hasSupplied = true;
    }

    if (internalIterator.hasNext()) {
      return internalIterator.next();
    } else {
      return endOfData();
    }
  }

  @Override
  public void close() throws Exception {
    if (internalIterator != null) {
      internalIterator.close();
    }
  }

  @Override
  public Optional<AirbyteStreamNameNamespacePair> getAirbyteStream() {
    return Optional.ofNullable(airbyteStream);
  }

}
