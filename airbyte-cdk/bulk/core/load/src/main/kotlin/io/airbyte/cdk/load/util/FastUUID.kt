package io.airbyte.cdk.load.util

import jakarta.inject.Singleton

@Singleton
class FastUUIDGenerator {
    val ng = java.util.Random(System.currentTimeMillis())

    fun insecureUUID(): String {
        val randomBytes = ByteArray(16)
        ng.nextBytes(randomBytes)
        randomBytes[6] = (randomBytes[6].toInt() and 0x0f).toByte() /* clear version        */
        randomBytes[6] = (randomBytes[6].toInt() or 0x40).toByte() /* set to version 4     */
        randomBytes[8] = (randomBytes[8].toInt() and 0x3f).toByte() /* clear variant        */
        randomBytes[8] =
            (randomBytes[8].toInt() or 0x80.toByte().toInt()).toByte() /* set to IETF variant  */
        return String(randomBytes)
    }
}
