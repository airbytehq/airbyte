/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * Consumes elements and saves them into a list. This list can be accessed at anytime. Because this
 * class stores everything it consumes in memory, it must be used carefully (the original use case
 * is for testing interfaces that operate on consumers)
 *
 * @param <T> type of the consumed elements
 */
public class ListConsumer<T> implements Consumer<T> {

  private final List<T> consumed;

  public ListConsumer() {
    this.consumed = new ArrayList<>();
  }

  @Override
  public void accept(final T t) {
    consumed.add(t);
  }

  public List<T> getConsumed() {
    return new ArrayList<>(consumed);
  }

}
