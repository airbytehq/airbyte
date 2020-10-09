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
