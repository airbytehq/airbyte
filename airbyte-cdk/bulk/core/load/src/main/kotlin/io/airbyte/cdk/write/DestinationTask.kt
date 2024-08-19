package io.airbyte.cdk.write

import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.delay

data class Concurrency(
    val scopeId: String,
    val perSync: Int = 0,
    val perStream: Int = 0,
    val exclusions: Set<String> = emptySet()
)

/**
 * A task or block of tasks that returns a value.
 *
 * T is the value returned by executing all underlying tasks
 * U is the value returned by running the individual task
 *
 * For Control Tasks
 *   * T is the "underlying value" (returned by a nested DestinationTask)
 *   * U is a list of Task(s) that return T (or return tasks that return T)
 * For DestinationTasks
 *   * U==T (ie, the "underlying value" is the same as the value returned)
 */
abstract class AbstractDestinationTask<T, out U> {
    /**
     * A task that when executed yields a task generated
     * from the underlying value of another task. The client
     * will never need to create or extend this directly.
     */
    abstract class FromValue<T, U>: ControlTask<U, AbstractDestinationTask<U, *>>()

    /**
     * A task that when executed yields a task generated
     * from the underlying task itself. The client will never
     * need to create or extend this directly.
     */
    abstract class FromTask<T, U>: ControlTask<U, AbstractDestinationTask<U, *>>()

    /**
     * Execute the task and return the value.
     */
    abstract suspend fun execute(): U

    /**
     * Given a function from this task's underlying value to another task,
     * yield a task that when executed (or when all underlying tasks are executed),
     * returns a list of tasks generated from the returned value(s).
     */
    abstract fun <V, W : AbstractDestinationTask<V, *>> mapValue(taskFor: (T) -> W): FromValue<T, V>

    /**
     * Given a function from this task to another task,
     * yield a task that when executed (or when all underlying tasks are executed),
     * returns a list of tasks generated from the underlying task.
     */
    abstract fun <V, W : AbstractDestinationTask<V, *>> mapTask(taskFor: (AbstractDestinationTask<T, *>) -> W): FromTask<T, V>
}

/**
 * Control Task
 *
 * Any task that returns a list of tasks when executed. The scheduler will immediately
 * enqueue all the returned tasks.
 */
abstract class ControlTask<T, out U: AbstractDestinationTask<T, *>>: AbstractDestinationTask<T, List<U>>() {
    abstract override suspend fun execute(): List<U>

    /**
     * Wrap this task in a task that passes the underlying managed value
     * to the next task.
     */
    override fun <V, W: AbstractDestinationTask<V, *>> mapValue(taskFor: (T) -> W): FromValue<T, V> {
        return FromUnderlyingValue(this, taskFor)
    }

    /**
     * Wrap this task in a task that passes the underlying task
     */
    override fun <V, W: AbstractDestinationTask<V, *>> mapTask(taskFor: (AbstractDestinationTask<T, *>) -> W): FromTask<T, V> {
        return FromControlTask(this, taskFor)
    }

    /**
     * Private implementation of FromValue specifically for control tasks: it
     * executes the underlying task and then wraps the returned tasks in `taskFor`
     */
    private class FromUnderlyingValue<T, U, V: AbstractDestinationTask<T, *>>(
        private val fromTask: ControlTask<T, V>,
        private val taskFor: (T) -> AbstractDestinationTask<U, *>
    ): FromValue<T, U>() {
        override suspend fun execute(): List<AbstractDestinationTask<U, *>> {
            val nextTasks = fromTask.execute()
            val wrapped = nextTasks.map { it.mapValue(taskFor) }
            return wrapped
        }
    }

    /**
     * Private implementation of FromTask specifically for control tasks: it
     * executes the underlying task and then wraps the returned tasks in `taskFor`
     */
    private class FromControlTask<T, U, V: AbstractDestinationTask<T, *>, W: AbstractDestinationTask<U, *>>(
        private val fromTask: ControlTask<T, V>,
        private val taskFor: (V) -> W
    ): FromTask<T, U>() {
        override suspend fun execute(): List<W> {
            val nextTasks = fromTask.execute()
            val mapped = nextTasks.map { taskFor(it) }
            return mapped
        }
    }
}

/**
 * Any task that returns a value when executed. The scheduler will not do anything
 * with the returned value nor will it enqueue another task.
 */
abstract class DestinationTask<T>: AbstractDestinationTask<T, T>() {
    open val concurrency: Concurrency? = null

    /**
     * Wrap this task in a task that passes the returned value to the next task.
     */
    override fun <V, W: AbstractDestinationTask<V, *>> mapValue(taskFor: (T) -> W): FromValue<T, V> {
        return FromReturnValue(this, taskFor)
    }

    override fun <V, W: AbstractDestinationTask<V, *>> mapTask(taskFor: (AbstractDestinationTask<T, *>) -> W): FromTask<T, V> {
        return FromDestinationTask(this, taskFor)
    }

    /**
     * Private implementation of FromValue specifically for destination tasks: it
     * executes the underlying task and then returns a singleton list of tasks from
     * applying `taskFor` to the returned value.
     */
    private class FromReturnValue<T, U>(
        private val fromTask: DestinationTask<T>,
        private val taskFor: (T) -> AbstractDestinationTask<U, *>
    ): FromValue<T, U>() {
        override suspend fun execute(): List<AbstractDestinationTask<U, *>> {
            val rval = fromTask.execute()
            return listOf(taskFor(rval))
        }
    }

    /**
     * Private implementation of FromTask specifically for destination tasks: it
     * executes the underlying task and then returns a singleton list of tasks from
     * applying `taskFor` to the underlying task.
     */
    private class FromDestinationTask<T, U>(
        private val fromTask: DestinationTask<T>,
        private val taskFor: (AbstractDestinationTask<T, T>) -> AbstractDestinationTask<U, *>): FromTask<T, U>() {
        override suspend fun execute(): List<AbstractDestinationTask<U, *>> {
            val nextTask = taskFor(fromTask)
            return listOf(nextTask)
        }
    }
}

/**
 * Ensure that the provided function is executed
 * before the task is executed.
 */
class Before<T, U: AbstractDestinationTask<T, *>>(
    private val before: suspend () -> Unit,
    private val underlyingTask: () -> ControlTask<T, U>,
): ControlTask<T, U>() {
    override suspend fun execute(): List<U> {
        before()
        return underlyingTask().execute()
    }
}

/**
 * Creates a task B from a task A which when executed
 * yields task A for execution. Its intended use is for
 * promoting DestinationTasks to ControlTasks in contexts
 * where a ControlTask is required.
 */
class Do<T, U: AbstractDestinationTask<T, *>>(
    private val underlyingTask: () -> U
): ControlTask<T, U>() {
    override suspend fun execute(): List<U> {
        return listOf(underlyingTask())
    }
}

class Done<T, U: AbstractDestinationTask<T, *>>: ControlTask<T, U>() {
    override suspend fun execute(): List<U> {
        return emptyList()
    }
}

/**
 * A control task which when executed, yields a task constructed
 * from the provided function.
 */
class Execute<T>(
    private val block: suspend () -> T
): DestinationTask<T>() {
    override suspend fun execute(): T {
        return block()
    }
}

/**
 * A control task which when executed, yields a list (not a TaskList)
 * of tasks constructed from the provided values. Each will be enqueued
 * immediately (unlike TaskLisk, which guarantees sequential execution).
 */
open class ForEach<T, U, V: AbstractDestinationTask<U, *>>(
    private val values: List<T>,
    private val taskFor: (T) -> V
): ControlTask<U, V>() {
    override suspend fun execute(): List<V> {
        return values.map { taskFor(it) }
    }
}

/**
 * A control task which when executed, yields a list
 * of tasks constructed from the streams in the catalog.
 */
class ForEachStream<T, U: AbstractDestinationTask<T, *>>(
    taskFor: (Stream) -> U
): ForEach<Stream, T, U>(DummyCatalog().streams, taskFor)

class Noop: DestinationTask<Unit>() {
    override suspend fun execute() {}
}

/**
 * A control task which when executed, repeatedly
 * executes the task provided by calling `taskFor`
 * iteratively on its own output (primed with `initial`)
 * until `terminalCondition` returns True.
 *
 * The provided task will always be executed at least once,
 * even if `initial` meets the terminal condition.
 */
open class IterateUntil<T, U: AbstractDestinationTask<T, *>>(
    private val initial: T,
    private val terminalCondition: (T) -> Boolean,
    private val taskFor: (T) -> U
): ControlTask<T, AbstractDestinationTask.FromValue<T, T>>() {
    override suspend fun execute(): List<FromValue<T, T>> {
        return listOf(
            taskFor(initial).mapValue { value ->
                if (terminalCondition(value)) {
                    Return(value)
                } else {
                    IterateUntil(value, terminalCondition, taskFor)
                }
            }
        )
    }
}

class IterateUntilNull<T, U: AbstractDestinationTask<T?, *>>(
    private val initial: T,
    private val taskFor: (T) -> U
): IterateUntil<T?, U>(initial, { it == null }, { taskFor(it!!) })

/**
 * Ensure that all tasks dispatched by the underlying
 * control task complete before this task is considered
 * complete.
 *
 * This works because of the way the scheduler enqueues
 * tasks: it will not enqueue the next task until the
 * current task is complete.
 */
class Join<T, U: AbstractDestinationTask<T, *>>(
    private val underlying: () -> ControlTask<T, U>
): ControlTask<T, AbstractDestinationTask.FromValue<T, T>>() {
    val taskCount = AtomicInteger(0)

    override suspend fun execute(): List<FromValue<T, T>> {
        val acquire = underlying().mapTask { task ->
                Before({taskCount.incrementAndGet()}) {
                    Do { task }
                }
            }
        val thenReleaseAndWait = acquire.mapValue { value ->
            Before({
                taskCount.decrementAndGet()
                while (taskCount.get() > 0) {
                    delay(100)
                }
            }) {
                Do { Return(value) }
            }
        }
        return listOf(thenReleaseAndWait)
    }
}

class NotUntil<T, U: AbstractDestinationTask<T, *>>(
    private val predicate: () -> Boolean,
    private val underlyingTask: () -> AbstractDestinationTask<T, *>,
): ControlTask<T, AbstractDestinationTask<T, *>>() {
    override suspend fun execute(): List<AbstractDestinationTask<T, *>> {
        if (!predicate()) {
            return listOf(this)
        }
        return listOf(underlyingTask())
    }
}

/**
 * A control task which yields 0..(N-1) tasks,
 * constructed from the task index.
 */
class Replicated<T, U: AbstractDestinationTask<T, *>>(
    val count: Int,
    val taskFor: (Int) -> U
): ForEach<Int, T, U>((0 until count).toList(), taskFor)

/**
 * A task which returns the provided value. Its
 * intended use is for promoting values to tasks
 * in contexts where a task is required.
 */
class Return<T>(
    private val value: T
): DestinationTask<T>() {
    override suspend fun execute(): T {
        return value
    }
}

/**
 * A control task which when guarantees sequential execution
 * of the provided tasks. (Each task when executes returns
 * a task which executes all tasks underlying the head
 * of the list and returns the tail as a new TaskList.)
 */
class TaskList<T, U: AbstractDestinationTask<T, *>>(
    private val tasks: List<U>
): ControlTask<T, ControlTask<T, *>>() {
    override suspend fun execute(): List<ControlTask<T, *>> {
        if (tasks.isEmpty()) {
            return emptyList()
        } else {
            val headGuarded = Join {
                Do { tasks.first() }
            }
            val withTail = headGuarded.mapValue { value ->
                TaskSet(listOf(
                    Return(value),
                    TaskList(tasks.drop(1))))
            }
            return listOf(withTail)
        }
    }
}

/**
 * Control task which when executed, will cause all the underlying
 * tasks to be enqueued. (This is different from the TaskList,
 * which guarantees sequential execution.)
 */
class TaskSet<T, U: AbstractDestinationTask<T, *>>(
    private val tasks: List<U>
): ControlTask<T, U>() {
    override suspend fun execute(): List<U> {
        return tasks
    }
}

open class Until<T, U: AbstractDestinationTask<T, *>>(
    private val predicate: () -> Boolean,
    private val underlyingTask: () -> ControlTask<T, U>,
): ControlTask<T, U>() {
    override suspend fun execute(): List<U> {
        if (!predicate()) {
            return emptyList()
        }
        return underlyingTask().execute()
    }
}

class UntilStreamComplete<T, U: AbstractDestinationTask<T, *>>(
    private val stream: Stream,
    private val underlyingTask: () -> ControlTask<T, U>,
): Until<T, U>({ MessageQueue.instance.isStreamComplete(stream) }, underlyingTask)


/**
 * A task which reruns an underlying task until
 * the underlying value yielded passes a predicate
 */
class UntilUnderlying<T, U: AbstractDestinationTask<T, *>>(
    private val predicate: (T) -> Boolean,
    private val underlyingTask: () -> U
): ControlTask<T, AbstractDestinationTask.FromValue<T, T>>() {
    override suspend fun execute(): List<FromValue<T, T>> {
        return listOf(
            underlyingTask().mapValue { value ->
                if (predicate(value)) {
                    Return(value)
                } else {
                    underlyingTask()
                }
            }
        )
    }
}
