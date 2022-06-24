/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.google.common.collect.ImmutableList;
import io.airbyte.commons.concurrency.VoidCallable;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class CompositeIteratorTest {

  private VoidCallable onClose1;
  private VoidCallable onClose2;
  private VoidCallable onClose3;

  @BeforeEach
  void setup() {
    onClose1 = mock(VoidCallable.class);
    onClose2 = mock(VoidCallable.class);
    onClose3 = mock(VoidCallable.class);
  }

  @Test
  void testNullInput() {
    assertThrows(NullPointerException.class, () -> new CompositeIterator<>(null));
  }

  @Test
  void testEmptyInput() {
    final AutoCloseableIterator<String> iterator = new CompositeIterator<>(Collections.emptyList());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testMultipleIterators() throws Exception {
    final AutoCloseableIterator<String> iterator = new CompositeIterator<>(ImmutableList.of(
        AutoCloseableIterators.fromIterator(MoreIterators.of("a", "b", "c"), onClose1),
        AutoCloseableIterators.fromIterator(MoreIterators.of("d", "e", "f"), onClose2),
        AutoCloseableIterators.fromIterator(MoreIterators.of("g", "h", "i"), onClose3)));

    assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1, onClose2, onClose3));
    assertNext(iterator, "a");
    assertNext(iterator, "b");
    assertNext(iterator, "c");
    assertNext(iterator, "d");
    assertOnCloseInvocations(ImmutableList.of(onClose1), ImmutableList.of(onClose2, onClose3));
    assertNext(iterator, "e");
    assertNext(iterator, "f");
    assertNext(iterator, "g");
    assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2), ImmutableList.of(onClose3));
    assertNext(iterator, "h");
    assertNext(iterator, "i");
    assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2), ImmutableList.of(onClose3));
    assertFalse(iterator.hasNext());
    assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2, onClose3), ImmutableList.of());

    iterator.close();

    verify(onClose1, times(1)).call();
    verify(onClose2, times(1)).call();
    verify(onClose3, times(1)).call();
  }

  @Test
  void testWithEmptyIterators() throws Exception {
    final AutoCloseableIterator<String> iterator = new CompositeIterator<>(ImmutableList.of(
        AutoCloseableIterators.fromIterator(MoreIterators.of("a", "b", "c"), onClose1),
        AutoCloseableIterators.fromIterator(MoreIterators.of(), onClose2),
        AutoCloseableIterators.fromIterator(MoreIterators.of("g", "h", "i"), onClose3)));

    assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1, onClose2, onClose3));
    assertNext(iterator, "a");
    assertNext(iterator, "b");
    assertNext(iterator, "c");
    assertNext(iterator, "g");
    assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2), ImmutableList.of(onClose3));
    assertNext(iterator, "h");
    assertNext(iterator, "i");
    assertFalse(iterator.hasNext());
    assertOnCloseInvocations(ImmutableList.of(onClose1, onClose2, onClose3), ImmutableList.of());
  }

  @Test
  void testCloseBeforeUsingItUp() throws Exception {
    final AutoCloseableIterator<String> iterator = new CompositeIterator<>(ImmutableList.of(
        AutoCloseableIterators.fromIterator(MoreIterators.of("a", "b", "c"), onClose1)));

    assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1));
    assertNext(iterator, "a");
    assertNext(iterator, "b");
    assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1));
    iterator.close();
    assertOnCloseInvocations(ImmutableList.of(onClose1), ImmutableList.of());
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testCannotOperateAfterClosing() throws Exception {
    final AutoCloseableIterator<String> iterator = new CompositeIterator<>(ImmutableList.of(
        AutoCloseableIterators.fromIterator(MoreIterators.of("a", "b", "c"), onClose1)));

    assertOnCloseInvocations(ImmutableList.of(), ImmutableList.of(onClose1));
    assertNext(iterator, "a");
    assertNext(iterator, "b");
    iterator.close();
    assertThrows(IllegalStateException.class, iterator::hasNext);
    assertThrows(IllegalStateException.class, iterator::next);
    iterator.close(); // still allowed to close again.
  }

  private void assertNext(final Iterator<String> iterator, final String value) {
    assertTrue(iterator.hasNext());
    assertEquals(value, iterator.next());
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
