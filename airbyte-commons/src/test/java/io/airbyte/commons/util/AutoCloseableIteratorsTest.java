/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterators;
import io.airbyte.commons.concurrency.VoidCallable;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class AutoCloseableIteratorsTest {

  @Test
  void testFromIterator() throws Exception {
    final VoidCallable onClose = mock(VoidCallable.class);
    final AutoCloseableIterator<String> iterator = AutoCloseableIterators.fromIterator(MoreIterators.of("a", "b", "c"), onClose);

    assertNext(iterator, "a");
    assertNext(iterator, "b");
    assertNext(iterator, "c");
    iterator.close();

    verify(onClose).call();
  }

  @Test
  void testFromStream() throws Exception {
    final AtomicBoolean isClosed = new AtomicBoolean(false);
    final Stream<String> stream = Stream.of("a", "b", "c");
    stream.onClose(() -> isClosed.set(true));

    final AutoCloseableIterator<String> iterator = AutoCloseableIterators.fromStream(stream);

    assertNext(iterator, "a");
    assertNext(iterator, "b");
    assertNext(iterator, "c");
    iterator.close();

    assertTrue(isClosed.get());
  }

  private void assertNext(final Iterator<String> iterator, final String value) {
    assertTrue(iterator.hasNext());
    assertEquals(value, iterator.next());
  }

  @Test
  void testAppendOnClose() throws Exception {
    final VoidCallable onClose1 = mock(VoidCallable.class);
    final VoidCallable onClose2 = mock(VoidCallable.class);

    final AutoCloseableIterator<Integer> iterator = AutoCloseableIterators.fromIterator(MoreIterators.of(1, 2, 3), onClose1);
    final AutoCloseableIterator<Integer> iteratorWithExtraClose = AutoCloseableIterators.appendOnClose(iterator, onClose2);

    iteratorWithExtraClose.close();
    verify(onClose1).call();
    verify(onClose2).call();
  }

  @Test
  void testTransform() {
    final Iterator<Integer> transform = Iterators.transform(MoreIterators.of(1, 2, 3), i -> i + 1);
    assertEquals(ImmutableList.of(2, 3, 4), MoreIterators.toList(transform));
  }

  @Test
  void testConcatWithEagerClose() throws Exception {
    final VoidCallable onClose1 = mock(VoidCallable.class);
    final VoidCallable onClose2 = mock(VoidCallable.class);

    final AutoCloseableIterator<String> iterator = new CompositeIterator<>(ImmutableList.of(
        AutoCloseableIterators.fromIterator(MoreIterators.of("a", "b"), onClose1),
        AutoCloseableIterators.fromIterator(MoreIterators.of("d"), onClose2)));

    assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1, onClose2));
    assertNext(iterator, "a");
    assertNext(iterator, "b");
    assertNext(iterator, "d");
    assertOnCloseInvocations(ImmutableList.of(onClose1), ImmutableList.of(onClose2));
    assertFalse(iterator.hasNext());
    assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2), ImmutableList.of());

    iterator.close();

    verify(onClose1, times(1)).call();
    verify(onClose2, times(1)).call();
  }

  private void assertOnCloseInvocations(final List<VoidCallable> haveClosed, final List<VoidCallable> haveNotClosed) throws Exception {
    for (final VoidCallable voidCallable : haveClosed) {
      verify(voidCallable).call();
    }

    for (final VoidCallable voidCallable : haveNotClosed) {
      verify(voidCallable, never()).call();
    }
  }

}
