/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.transform

import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.micronaut.context.ApplicationContext
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Test

/**
 * Guards the DI contract: the CDK ships a `@Secondary` `NoOpCoercer`, so resolving [ValueCoercer]
 * must pick our `@Singleton` [StarrocksValueCoercer]. Catches a silent regression if the override
 * mechanism ever changes (e.g. a stray `@Replaces`/`@Primary`).
 */
class StarrocksValueCoercerWiringTest {

    @Test
    fun `the active ValueCoercer bean is StarrocksValueCoercer`() {
        ApplicationContext.builder().eagerInitSingletons(false).build().start().use { ctx ->
            assertInstanceOf(
                StarrocksValueCoercer::class.java,
                ctx.getBean(ValueCoercer::class.java)
            )
        }
    }
}
