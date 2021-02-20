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
  public void accept(T t) {
    consumed.add(t);
  }

  public List<T> getConsumed() {
    return new ArrayList<>(consumed);
  }

}
