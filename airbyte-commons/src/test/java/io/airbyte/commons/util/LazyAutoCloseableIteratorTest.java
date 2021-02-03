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
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import java.util.Collections;
import java.util.Iterator;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class LazyAutoCloseableIteratorTest {

  private AutoCloseableIterator<String> internalIterator;
  private Supplier<AutoCloseableIterator<String>> iteratorSupplier;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    internalIterator = (AutoCloseableIterator<String>) mock(AutoCloseableIterator.class);
    iteratorSupplier = mock(Supplier.class);
    when(iteratorSupplier.get()).thenReturn(internalIterator);
  }

  @Test
  void testNullInput() {
    assertThrows(NullPointerException.class, () -> new LazyAutoCloseableIterator<>(null));
    final AutoCloseableIterator<String> iteratorWithNullSupplier = new LazyAutoCloseableIterator<>(() -> null);
    assertThrows(NullPointerException.class, iteratorWithNullSupplier::next);
  }

  @Test
  void testEmptyInput() throws Exception {
    mockInternalIteratorWith(Collections.emptyIterator());
    final AutoCloseableIterator<String> iterator = new LazyAutoCloseableIterator<>(iteratorSupplier);

    assertFalse(iterator.hasNext());
    iterator.close();
    verify(internalIterator).close();
  }

  @Test
  void test() throws Exception {
    mockInternalIteratorWith(MoreIterators.of("a", "b", "c"));

    final AutoCloseableIterator<String> iterator = new LazyAutoCloseableIterator<>(iteratorSupplier);
    verify(iteratorSupplier, never()).get();
    assertNext(iterator, "a");
    verify(iteratorSupplier).get();
    verifyNoMoreInteractions(iteratorSupplier);
    assertNext(iterator, "b");
    assertNext(iterator, "c");
    iterator.close();
    verify(internalIterator).close();
  }

  @Test
  void testCloseBeforeSupply() throws Exception {
    mockInternalIteratorWith(MoreIterators.of("a", "b", "c"));
    final AutoCloseableIterator<String> iterator = new LazyAutoCloseableIterator<>(iteratorSupplier);
    iterator.close();
    verify(iteratorSupplier, never()).get();
  }

  private void mockInternalIteratorWith(Iterator<String> iterator) {
    when(internalIterator.hasNext()).then((a) -> iterator.hasNext());
    when(internalIterator.next()).then((a) -> iterator.next());
  }

  private void assertNext(Iterator<String> iterator, String value) {
    assertTrue(iterator.hasNext());
    assertEquals(value, iterator.next());
  }

}
