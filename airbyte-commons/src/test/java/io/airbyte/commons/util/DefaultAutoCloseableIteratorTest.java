/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.concurrency.VoidCallable;
import java.util.Collections;
import java.util.Iterator;
import org.junit.jupiter.api.Test;

class DefaultAutoCloseableIteratorTest {

  @Test
  void testNullInput() {
    final VoidCallable onClose = mock(VoidCallable.class);
    assertThrows(NullPointerException.class, () -> new DefaultAutoCloseableIterator<>(null, onClose, null));
    assertThrows(NullPointerException.class, () -> new DefaultAutoCloseableIterator<>(Collections.emptyIterator(), null, null));
    assertThrows(NullPointerException.class, () -> new DefaultAutoCloseableIterator<>(null, null, null));
  }

  @Test
  void testEmptyInput() throws Exception {
    final VoidCallable onClose = mock(VoidCallable.class);
    final AutoCloseableIterator<String> iterator = new DefaultAutoCloseableIterator<>(Collections.emptyIterator(), onClose, null);
    assertFalse(iterator.hasNext());
    iterator.close();
    verify(onClose).call();
  }

  @Test
  void test() throws Exception {
    final VoidCallable onClose = mock(VoidCallable.class);
    final AutoCloseableIterator<String> iterator = new DefaultAutoCloseableIterator<>(MoreIterators.of("a", "b", "c"), onClose, null);

    assertNext(iterator, "a");
    assertNext(iterator, "b");
    assertNext(iterator, "c");
    iterator.close();

    verify(onClose).call();
  }

  @Test
  void testCannotOperateAfterClosing() throws Exception {
    final VoidCallable onClose = mock(VoidCallable.class);
    final AutoCloseableIterator<String> iterator = new DefaultAutoCloseableIterator<>(MoreIterators.of("a", "b", "c"), onClose, null);

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

}
