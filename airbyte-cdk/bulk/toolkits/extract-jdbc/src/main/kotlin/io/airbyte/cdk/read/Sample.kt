/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

/** Convenience object for maintaining sampled data and its accompanying metadata. */
data class Sample<T>(
    val sampledValues: List<T>,
    val kind: Kind,
    val valueWeight: Long,
) {
    fun <U> map(fn: (T) -> U): Sample<U> = Sample(sampledValues.map(fn), kind, valueWeight)

    enum class Kind {
        EMPTY, // the table is empty;
        TINY, // the table has fewer rows than the target sample size;
        SMALL, // collecting the sample still requires a full table scan;
        MEDIUM, // collecting the sample is possible while sampling at ~0.3%;
        LARGE, // collecting the sample is possible while sampling most aggressively.
    }
}
