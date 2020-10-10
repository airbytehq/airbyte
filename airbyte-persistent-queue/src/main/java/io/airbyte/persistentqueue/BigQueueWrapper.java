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

package io.airbyte.persistentqueue;

import com.google.common.base.Preconditions;
import com.leansoft.bigqueue.BigQueueImpl;
import com.leansoft.bigqueue.IBigQueue;
import java.io.IOException;
import java.nio.file.Path;

// BigQueue is threadsafe.
public class BigQueueWrapper extends AbstractCloseableInputQueue<byte[]> implements CloseableInputQueue<byte[]> {

  private final IBigQueue queue;

  public BigQueueWrapper(Path persistencePath, String queueName) throws IOException {
    queue = new BigQueueImpl(persistencePath.toString(), queueName);
  }

  @Override
  public boolean enqueueInternal(byte[] bytes) {
    try {
      queue.enqueue(bytes);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return true;
  }

  @Override
  protected byte[] pollInternal() {
    try {
      return queue.dequeue();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public byte[] peek() {
    Preconditions.checkState(!closed.get());
    try {
      return queue.peek();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public int size() {
    Preconditions.checkState(!closed.get());
    return Math.toIntExact(queue.size());
  }

  @Override
  protected void closeInternal() throws Exception {
    queue.close();
    queue.gc();
  }

}
