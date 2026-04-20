/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.ssh

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import org.apache.sshd.common.SshException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test

class TunnelSessionTest {

    @Test
    fun `timeout SshException is classified as transient`() {
        val cause =
            SshException(
                "failed to get operation result within specified timeout: 15000 MILLISECONDS",
            )

        val classified = classifySshTunnelException(cause)

        val transient =
            assertInstanceOf(
                TransientErrorException::class.java,
                classified,
                "SSH tunnel timeouts must be transient so that the platform retry budget handles them.",
            )
        assertSame(cause, transient.cause)
        assertEquals(SSH_TIMEOUT_DISPLAY_MESSAGE, transient.message)
        // Guard against regression: timeouts must not be classified as config errors.
        assertNotEquals(
            ConfigErrorException::class.java,
            classified.javaClass,
        )
    }

    @Test
    fun `timeout classification is case-insensitive`() {
        val cause =
            SshException(
                "Failed To Get Operation Result Within Specified Timeout",
            )

        val classified = classifySshTunnelException(cause)

        assertInstanceOf(TransientErrorException::class.java, classified)
    }

    @Test
    fun `non-timeout SshException falls through to RuntimeException`() {
        val cause = SshException("Connection refused by server")

        val classified = classifySshTunnelException(cause)

        assertEquals(RuntimeException::class.java, classified.javaClass)
        assertSame(cause, classified.cause)
    }

    @Test
    fun `display message drops remediation guidance`() {
        // Transient errors should not embed "please"-style remediation copy; that belongs in docs
        // and the retry UI, not in the message surfaced on a transient failure.
        assert(!SSH_TIMEOUT_DISPLAY_MESSAGE.lowercase().contains("please"))
    }
}
