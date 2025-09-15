/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import com.github.f4b6a3.uuid.alt.GUID
import jakarta.inject.Singleton
import java.util.UUID

/**
 * Custom UUID generator to avoid locking caused by the use of [java.security.SecureRandom] by the
 * JDK [UUID] implementation by using better-performing UUID generators.
 */
@Singleton
class UUIDGenerator {

    /**
     * Generates a UUID v4 random-based UUID. This method is up to 10 times faster than
     * [UUID.randomUUID].
     */
    fun v4(): UUID = GUID.v4().toUUID()

    /**
     * Generates a UUID v7 UUID with Unix epoch. This method is up to 10 times faster than
     * [UUID.randomUUID].
     */
    fun v7(): UUID = GUID.v7().toUUID()
}
