/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.featureflag

import org.junit.jupiter.api.Test

class EnvVarTest {
    @Test
    fun `verify undefined flag returns default`() {
        val ctx = User("")
        // defaults to false, undefined in env-var
        EnvVar(envVar = "undefined").apply { fetcher = { null } }.also {
            assert(!it.enabled(ctx))
        }
        // defaults to true, undefined in env-var
        EnvVar(envVar = "undefined", default = true).apply { fetcher = { null } }.also {
            assert(it.enabled(ctx))
        }
    }

    @Test
    fun `verify defined flag variable returns defined value`() {
        val envTrue = Pair("TEST_ENV_000", "true")
        val envFalse = Pair("TEST_ENV_001", "false")
        val envX = Pair("TEST_ENV_001", "x")

        val envVars = mapOf(envTrue, envFalse, envX)
        val testFetcher = { s: String -> envVars[s] }
        val ctx = User("")

        // defaults to false, but defined as true in the env-var
        EnvVar(envVar = envTrue.first)
            .apply { fetcher = testFetcher }
            .also { assert(it.enabled(ctx)) }

        // defaults to false, also defined as false in the env-var
        EnvVar(envVar = envFalse.first)
            .apply { fetcher = testFetcher }
            .also { assert(!it.enabled(ctx)) }

        // defaults to true, but defined as false in the env-var
        EnvVar(envVar = envFalse.first, default = true)
            .apply { fetcher = testFetcher }
            .also { assert(!it.enabled(ctx)) }

        // defaults to false, but defined incorrectly in env-var
        EnvVar(envVar = envX.first)
            .apply { fetcher = testFetcher }
            .also { assert(!it.enabled(ctx)) }

        // defaults to true, but defined incorrectly in env-var
        EnvVar(envVar = envX.first, default = true)
            .apply { fetcher = testFetcher }
            .also {
                // any value that is defined but not defined explicitly as "true" will return false
                assert(!it.enabled(ctx))
            }
    }
}
