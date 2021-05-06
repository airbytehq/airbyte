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

import static java.lang.Thread.sleep;

import io.airbyte.commons.lang.Queues;
import java.util.Iterator;
import java.util.concurrent.ArrayBlockingQueue;
import org.junit.jupiter.api.Test;

public class MoreIteratorsTest {

  @Test
  void test() {
    // Define capacity of ArrayBlockingQueue
    int capacity = 5;

    // Create object of ArrayBlockingQueue
    ArrayBlockingQueue<String> queue = new ArrayBlockingQueue<String>(capacity);

    final Thread thread = new Thread(() -> {
      int i = 0;
      while (true) {
        try {
          sleep(10);
        } catch (InterruptedException e) {
          throw new RuntimeException(e);
        }
        queue.offer("Human " + i++);
      }
    });

    thread.start();

    // Print queue
    System.out.println("Queue is " + queue);

    // Call iterator() method and Create an iterator
    // final Iterator iteratorValues = queue.iterator();

    final Iterator iteratorValues = Queues.toStream(queue).iterator();

    // Print elements of iterator
    System.out.println("\nThe iterator values:");
    while (iteratorValues.hasNext()) {
      System.out.println(iteratorValues.next());
    }
  }

}
