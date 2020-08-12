package io.dataline.workers.singer;

import org.junit.Test;

public class TestBaseSingerWorker {

  @Test
  public void testSuccessfulWorkerWithZeroExit() {}

  @Test
  public void testSuccessfulWorkerWithNonZeroExit() {}

  @Test
  public void testFailedWorker() {
    //    final RuntimeException failureReason =
    //        new RuntimeException("Failure is the predecessor of success");
    //    BaseSingerWorker failingSingerWorker =
    //        new BaseSingerWorker() {
    //          @Override
    //          protected Process runInternal() {
    //            throw failureReason;
    //          }
    //
    //          @Override
    //          protected Object getOutputInternal() {
    //            return null;
    //          }
    //        };
  }
}
