package io.airbyte.integrations.destination.shelby.http.job

enum class JobStatus {
    UPLOADED {
        override fun isTerminal(): Boolean = false
    },
    INGESTING {
        override fun isTerminal(): Boolean = false
    },
    COMPLETE {
        override fun isTerminal(): Boolean = true
    },
    INCOMPLETE {
        override fun isTerminal(): Boolean = true
    };

    abstract fun isTerminal(): Boolean
}
