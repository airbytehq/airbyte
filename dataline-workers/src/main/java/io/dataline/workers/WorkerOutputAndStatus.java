package io.dataline.workers;

public class WorkerOutputAndStatus<OutputType> {
    public final OutputType output;
    public final WorkerStatus status;

    public WorkerOutputAndStatus(OutputType output, WorkerStatus status) {
        this.output = output;
        this.status = status;
    }
}
