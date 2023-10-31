/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;

public class NoopTyperDeduper implements TyperDeduper {

  @Override
  public void prepareTables() {

  }

  @Override
  public void typeAndDedupe(final String originalNamespace, final String originalName, final boolean mustRun) {

  }

  @Override
  public Lock getRawTableInsertLock(final String originalNamespace, final String originalName) {
    // Return a fake lock that does nothing.
    return new Lock() {

      @Override
      public void lock() {

      }

      @Override
      public void lockInterruptibly() {

      }

      @Override
      public boolean tryLock() {
        // To mimic NoOp behavior always return true that lock is acquired
        return true;
      }

      @Override
      public boolean tryLock(final long time, final TimeUnit unit) {
        // To mimic NoOp behavior always return true that lock is acquired
        return true;
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
  public void commitFinalTables() {

  }

  @Override
  public void typeAndDedupe() {

  }

  @Override
  public void cleanup() {

  }

}
