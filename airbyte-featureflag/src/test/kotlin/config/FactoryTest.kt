/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag.config

import com.launchdarkly.sdk.server.LDClient
import io.airbyte.featureflag.CONFIG_FF_APIKEY
import io.airbyte.featureflag.CONFIG_FF_CLIENT
import io.airbyte.featureflag.CONFIG_FF_CLIENT_VAL_LAUNCHDARKLY
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Test
import kotlin.test.assertNotNull
import kotlin.test.assertNull

@MicronautTest(rebuildContext = true)
class FactoryTest {
    @Inject
    var ldClient: LDClient? = null

    @Test
    fun `LDClient is null when property is not defined`() {
        assertNull(ldClient)
    }

    @Test
    @Property(name = CONFIG_FF_CLIENT, value = CONFIG_FF_CLIENT_VAL_LAUNCHDARKLY)
    @Property(name = CONFIG_FF_APIKEY, value = "api-key")
    fun `LDClient is not null when property is defined`() {
        assertNotNull(ldClient)
    }

    @Test
    @Property(name = CONFIG_FF_CLIENT, value = "random-value")
    @Property(name = CONFIG_FF_APIKEY, value = "api-key")
    fun `LDClient is null when property is defined but incorrectly`() {
        assertNull(ldClient)
    }
}
