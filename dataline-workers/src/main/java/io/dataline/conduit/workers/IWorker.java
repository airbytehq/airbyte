package io.dataline.conduit.workers;

public interface IWorker<OutputType> {
    WorkerStatus getStatus();

    void run();

    OutputType getOutput();

    void cancel();
}
