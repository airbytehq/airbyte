/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;

public class NoopTyperDeduper implements TyperDeduper {

  @Override
  public void prepareTables() throws Exception {

  }

  @Override
  public void typeAndDedupe(final String originalNamespace, final String originalName, final boolean mustRun) throws Exception {

  }

  @Override
  public Lock getRawTableInsertLock(final String originalNamespace, final String originalName) {
    // Return a fake lock that does nothing.
    return new Lock() {

      @Override
      public void lock() {

      }

      @Override
      public void lockInterruptibly() throws InterruptedException {

      }

      @Override
      public boolean tryLock() {
        return false;
      }

      @Override
      public boolean tryLock(final long time, final TimeUnit unit) throws InterruptedException {
        return false;
      }

      @Override
      public void unlock() {

      }

      @Override
      public Condition newCondition() {
        return null;
      }

    };
  }

  @Override
  public void commitFinalTables() throws Exception {

  }

  @Override
  public void typeAndDedupe() throws Exception {

  }

  @Override
  public void cleanup() {

  }

}
