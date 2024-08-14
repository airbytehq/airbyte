package io.airbyte.cdk.write

import kotlin.math.min

/**
 * A task that can be executed by a DestinationRunner.
 *
 * concurrency: reports the desired concurrency:
 * - id: a unique identifier for the task
 * - perSync: the maximum number of tasks that can run concurrently in a sync
 * - perStream: the maximum number of tasks that can run concurrently for a single stream
 *
 * If perSync or perStream is 0, the task will never be blocked by that concurrency limit.
 * If concurrency is null, the task will always run.
 *
 * execute: executes the task and returns the next task to run.
 */
abstract class DestinationTask {
    data class Concurrency(val id: String, val perSync: Int=0, val perStream: Int=0) {
        fun available(): Int {
            if (perStream > 0 && perSync > 0) {
                return min(perStream, perSync)
            } else if (perStream > 0) {
                return perStream
            } else if (perSync > 0) {
                return perSync
            } else {
                return 0
            }
        }
    }
    open val concurrency: Concurrency? = null // null => always run

    abstract fun execute(): DestinationTask
}

/**
 * A task that controls the flow of execution. It is not itself executed.
 * Rather, it guards, fans out, or resource-counts other tasks.
 */
abstract class ControlTask: DestinationTask() {
    override fun execute(): DestinationTask {
        throw IllegalStateException("Control tasks should not be executed")
    }
}

/**
 * A task that is affined to single stream.
 */
interface PerStream {
    val stream: Stream
}

/**
 * The implementing task will be provided with the reader end of
 * a queue for its stream.
 */
interface RecordConsumer: PerStream {
    var payload: Iterable<DestinationRecord>?
    var endOfStream: Boolean
    var forceFlush: Boolean
}

/**
 * Control task that halts all task execution.
 */
class Done: ControlTask()

/**
 * Fan-out task that enqueues an instance of the underlying task for each stream.
 */
class ForEachStream(val taskFor: (Stream) -> DestinationTask): ControlTask()

/**
 * Fan-out task that enqueues an instance of the underlying task for the
 * amount of available parallelism (ie, min(perSync, perStream)).
 */
class ForEachAvailable(val taskFor: (Int) -> DestinationTask): ControlTask()

/**
 * The runner re-enqueues this task until the associated stream is complete
 */
class WhenStreamComplete(
    override val stream: Stream,
    val getTask: () -> DestinationTask
): ControlTask(), PerStream

/**
 * The runner will discard this task if any with the same id have run.
 */
class ExactlyOnce(
    val id: String,
    val task: () -> DestinationTask
): ControlTask()

/**
 * The runner will re-enqueue this task until the counter associated
 * with the id reaches 0.
 */
class WhenAllComplete(
    val id: String,
    val task: () -> DestinationTask
): ControlTask()

/**
 * The runner will increment the counter associated with the id before running the task.
 */
class Incrementing(
    val id: String,
    val task: () -> DestinationTask
): ControlTask()

/**
 * The runner will decrement the counter associated with the id before running the task.
 */
class Decrementing(
    val id: String,
    val task: () -> DestinationTask
): ControlTask()


