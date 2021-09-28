/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import java.util.Iterator;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public class MoreStreams {

  public static <T> Stream<T> toStream(Iterator<T> iterator) {
    return StreamSupport.stream(Spliterators.spliteratorUnknownSize(iterator, Spliterator.ORDERED), false);
  }

  public static <T> Stream<T> toStream(Iterable<T> iterable) {
    return toStream(iterable.iterator());
  }

}
