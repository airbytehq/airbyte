/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.featureflag.EnvVar
import org.junit.jupiter.api.Test

class EnvVarTest {
    @Test
    fun `verify undefined flag returns default`() {
        // defaults to false, undefined in env-var
        EnvVar(envVar = "undefined") { _ -> null }.also {
            assert(!it.enabled())
        }
        // defaults to true, undefined in env-var
        EnvVar(envVar = "undefined", default = true) { _ -> null }.also {
            assert(it.enabled())
        }
    }

    @Test
    fun `verify defined flag variable returns defined value`() {
        val envTrue = Pair("TEST_ENV_000", "true")
        val envFalse = Pair("TEST_ENV_001", "false")
        val envX = Pair("TEST_ENV_001", "x")

        val envVars = mapOf(envTrue, envFalse, envX)
        val fetcher = { s: String -> envVars[s] }

        // defaults to false, but defined as true in the env-var
        EnvVar(envVar = envTrue.first, fetcher = fetcher).also {
            assert(it.enabled())
        }
        // defaults to false, also defined as false in the env-var
        EnvVar(envVar = envFalse.first, fetcher = fetcher).also {
            assert(!it.enabled())
        }
        // defaults to true, but defined as false in the env-var
        EnvVar(envVar = envFalse.first, default = true, fetcher = fetcher).also {
            assert(!it.enabled())
        }
        // defaults to false, but defined incorrectly in env-var
        EnvVar(envVar = envX.first, fetcher = fetcher).also {
            assert(!it.enabled())
        }
        // defaults to true, but defined incorrectly in env-var
        EnvVar(envVar = envX.first, default = true, fetcher = fetcher).also {
            // any value that is defined but not defined explicitly as "true" will return false
            assert(!it.enabled())
        }
    }
}