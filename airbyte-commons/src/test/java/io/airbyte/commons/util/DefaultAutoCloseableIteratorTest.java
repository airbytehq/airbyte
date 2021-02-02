/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
    assertThrows(NullPointerException.class, () -> new DefaultAutoCloseableIterator<>(null, onClose));
    assertThrows(NullPointerException.class, () -> new DefaultAutoCloseableIterator<>(Collections.emptyIterator(), null));
    assertThrows(NullPointerException.class, () -> new DefaultAutoCloseableIterator<>(null, null));
  }

  @Test
  void testEmptyInput() throws Exception {
    final VoidCallable onClose = mock(VoidCallable.class);
    final AutoCloseableIterator<String> iterator = new DefaultAutoCloseableIterator<>(Collections.emptyIterator(), onClose);
    assertFalse(iterator.hasNext());
    iterator.close();
    verify(onClose).call();
  }

  @Test
  void test() throws Exception {
    final VoidCallable onClose = mock(VoidCallable.class);
    final AutoCloseableIterator<String> iterator = new DefaultAutoCloseableIterator<>(MoreIterators.of("a", "b", "c"), onClose);

    assertNext(iterator, "a");
    assertNext(iterator, "b");
    assertNext(iterator, "c");
    iterator.close();

    verify(onClose).call();
  }

  @Test
  void testCannotOperateAfterClosing() throws Exception {
    final VoidCallable onClose = mock(VoidCallable.class);
    final AutoCloseableIterator<String> iterator = new DefaultAutoCloseableIterator<>(MoreIterators.of("a", "b", "c"), onClose);

    assertNext(iterator, "a");
    assertNext(iterator, "b");
    iterator.close();
    assertThrows(IllegalStateException.class, iterator::hasNext);
    assertThrows(IllegalStateException.class, iterator::next);
    iterator.close(); // still allowed to close again.
  }

  private void assertNext(Iterator<String> iterator, String value) {
    assertTrue(iterator.hasNext());
    assertEquals(value, iterator.next());
  }

}
