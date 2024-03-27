package io.airbyte.cdk.components.cursor

import java.io.Serializable

@JvmRecord data class CursorState(
    val progress: Progress,
    val initialValues: List<Serializable>) : Comparable<CursorState> {

    enum class Progress {
        NOT_STARTED,
        ONGOING,
        DONE
    }

    override fun compareTo(other: CursorState): Int {
        val progressDelta = progress.ordinal - other.progress.ordinal
        if (progressDelta != 0 || progress != Progress.ONGOING) {
            return progressDelta
        }
        if (initialValues.zip(other.initialValues)
            .filter { (a, b) -> a != b }
            .isEmpty()) {
            return 0
        }
        return -1
    }

    companion object {
        @JvmStatic fun notStarted() = CursorState(Progress.NOT_STARTED, listOf())
        @JvmStatic fun ongoing(values: List<Serializable>) = CursorState(Progress.ONGOING, values)
        @JvmStatic fun done() = CursorState(Progress.DONE, listOf())

    }
}
