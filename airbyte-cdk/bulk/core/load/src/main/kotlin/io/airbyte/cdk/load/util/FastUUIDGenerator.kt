/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import jakarta.inject.Singleton
import java.nio.ByteBuffer
import java.util.UUID
import java.util.concurrent.ThreadLocalRandom

/**
 * Custom UUID generator to avoid locking caused by the use of [java.security.SecureRandom] by the
 * JDK [UUID] implementation. In testing, this implementation, while not cryptographically secure,
 * outperforms the secure implementation by about 4x. <p /> <p /> <b>N.B.</b> This generator should
 * only be used when a cryptographically secure UUID is not necessary.
 */
@Singleton
class FastUUIDGenerator {

    fun insecureUUID(): UUID {
        val randomBytes = ByteArray(16)

        // Ensure thread safe access to the random bytes.
        ThreadLocalRandom.current().nextBytes(randomBytes)

        val data = ByteBuffer.wrap(randomBytes)
        /* clear version */
        data.put(6, (data.get(6).toInt() and 0x0f).toByte())
        /* set to version 4 */
        data.put(6, (data.get(6).toInt() or 0x40).toByte())
        /* clear variant */
        data.put(8, (data.get(8).toInt() and 0x3f).toByte())
        /* set to IETF variant */
        data.put(8, (data.get(8).toInt() or 0x80.toByte().toInt()).toByte())

        // Constructors and Factories
        var msb: Long = 0
        var lsb: Long = 0
        assert(data.array().size == 16) { "data must be 16 bytes in length" }
        for (i in 0..7) msb = (msb shl 8) or (data[i].toInt() and 0xff).toLong()
        for (i in 8..15) lsb = (lsb shl 8) or (data[i].toInt() and 0xff).toLong()
        val mostSigBits = msb
        val leastSigBits = lsb

        return UUID(mostSigBits, leastSigBits)
    }
}
