package io.airbyte.cdk.write

import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.consumeAsFlow
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class DestinationTaskTest {
    @Test
    fun testTaskList() = runTest {
        val resultQueue = Channel<Int>(Channel.UNLIMITED)
        val limit = 1000
        val numberTasks = (0 until limit).map { Execute {
            delay((limit - it).toLong())
            resultQueue.send(it)
        } }
        val queueCloseTask = Execute { resultQueue.close() }.mapValue { _ -> Noop() }
        val tasks = TaskList(numberTasks + listOf(queueCloseTask))

        val runner = DestinationRunner(tasks)
        launch { runner.run() }
        val results = resultQueue.consumeAsFlow().toList()
        assert(results == (0 until limit).toList())
        runner.stop()
    }

    @Test
    fun testReplicate() = runTest {
        val resultQueue = Channel<Int>(Channel.UNLIMITED)
        val fanOut = 3
        val replicatedTask = Replicated(fanOut) { i ->
            Execute {
                delay((fanOut - i).toLong())
                println("sending $i")
                resultQueue.send(i)
            }
        }
        val queueCloseTask = Execute {
            println("Closing queue")
            //resultQueue.close()
        }.mapValue { _ -> Noop() }
        val tasks = TaskList(listOf(replicatedTask, queueCloseTask))
        val runner = DestinationRunner(tasks)
        launch { runner.run() }
        val results = resultQueue.consumeAsFlow().toList()
        println(results)
        runner.stop()
    }
}
