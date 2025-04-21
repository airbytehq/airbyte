package io.airbyte.cdk.load.util

import jakarta.inject.Singleton
import java.util.*

@Singleton
class FastUUIDGenerator {
    private val ng = Random(System.currentTimeMillis())

    fun insecureUUID(): UUID {
        val data = ByteArray(16)
        ng.nextBytes(data)
        data[6] = (data[6].toInt() and 0x0f).toByte() /* clear version        */
        data[6] = (data[6].toInt() or 0x40).toByte() /* set to version 4     */
        data[8] = (data[8].toInt() and 0x3f).toByte() /* clear variant        */
        data[8] =
            (data[8].toInt() or 0x80.toByte().toInt()).toByte() /* set to IETF variant  */
        // Turn into a hyphen-delimited human-readable uuid

        // Constructors and Factories
        var msb: Long = 0
        var lsb: Long = 0
        assert(data.size == 16) { "data must be 16 bytes in length" }
        for (i in 0..7) msb = (msb shl 8) or (data[i].toInt() and 0xff).toLong()
        for (i in 8..15) lsb = (lsb shl 8) or (data[i].toInt() and 0xff).toLong()
        val mostSigBits = msb
        val leastSigBits = lsb

        return UUID(mostSigBits, leastSigBits)
    }
}
