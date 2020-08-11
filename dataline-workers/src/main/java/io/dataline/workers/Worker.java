package io.dataline.workers;

public interface Worker<OutputType> {
    WorkerStatus getStatus();

    void run();

    OutputType getOutput();

    void cancel();
}
