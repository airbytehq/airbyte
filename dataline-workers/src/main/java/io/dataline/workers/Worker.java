package io.dataline.workers;

public interface Worker<OutputType> {
    WorkerStatus getStatus();

    /**
     * Blocking call to run the worker's workflow. Once this is complete, getStatus should return either COMPLETE, FAILED, or CANCELLED.
     */
    void run();

    /**
     * To be called once the process has reached a terminal status
     * @return
     */
    OutputType getOutput();

    void cancel();
}
