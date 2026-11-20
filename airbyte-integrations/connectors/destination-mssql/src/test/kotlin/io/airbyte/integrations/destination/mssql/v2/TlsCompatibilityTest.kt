/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class TlsCompatibilityTest {

    @Test
    fun `removes the entries added in JDK 21_0_10`() {
        assertEquals(
            CORRETTO_21_0_6,
            TlsCompatibility.relaxDisabledAlgorithms(CORRETTO_21_0_13),
        )
    }

    @Test
    fun `returns a value without those entries unchanged`() {
        assertEquals(CORRETTO_21_0_6, TlsCompatibility.relaxDisabledAlgorithms(CORRETTO_21_0_6))
    }

    @Test
    fun `tolerates odd spacing and case`() {
        assertEquals(
            "SSLv3, DH keySize < 1024, ECDH, rsa_pss_rsae_sha1, SHA1 usage SignedJAR",
            TlsCompatibility.relaxDisabledAlgorithms(
                "SSLv3,DH keySize < 1024 ,  tls_rsa_* ,ECDH,\tRSA_PKCS1_SHA1   usage\t" +
                    "handshakesignature,ecdsa_sha1 usage HandshakeSignature,, " +
                    "rsa_pss_rsae_sha1,SHA1 usage SignedJAR ",
            ),
        )
    }

    @Test
    fun `keeps cipher suites and usages that only look similar`() {
        val value =
            "TLS_RSA_WITH_AES_128_CBC_SHA, TLS_ECDHE_RSA_*, rsa_pkcs1_sha1 usage CertificateSignature"
        assertEquals(value, TlsCompatibility.relaxDisabledAlgorithms(value))
    }

    @Test
    fun `returns an empty value unchanged`() {
        assertEquals("", TlsCompatibility.relaxDisabledAlgorithms(""))
    }

    @Test
    fun `maps a handshake record to an INFO message`() {
        val handshake =
            TlsCompatibility.handshakeOf(
                HANDSHAKE_TEMPLATE,
                arrayOf<Any>(
                    "db.example.com",
                    1433,
                    "TLSv1.2",
                    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                    1778547583L,
                ),
            )
        assertEquals(
            TlsCompatibility.Handshake(
                "db.example.com",
                "1433",
                "TLSv1.2",
                "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            ),
            handshake,
        )
        assertFalse(handshake!!.isStaticRsa)
        assertEquals(
            "TLS handshake: peer=db.example.com:1433 protocol=TLSv1.2 " +
                "cipherSuite=TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            handshake.logMessage,
        )
    }

    @Test
    fun `maps a static-RSA handshake record to a WARN message`() {
        val handshake =
            TlsCompatibility.handshakeOf(
                "duration = 12.50 ms:$HANDSHAKE_TEMPLATE",
                arrayOf<Any>("10.0.0.7", 14330L, "TLSv1.2", "TLS_RSA_WITH_AES_256_GCM_SHA384", -1L),
            )
        assertTrue(handshake!!.isStaticRsa)
        assertEquals(
            "TLS handshake: peer=10.0.0.7:14330 protocol=TLSv1.2 " +
                "cipherSuite=TLS_RSA_WITH_AES_256_GCM_SHA384 (static-RSA key exchange: no " +
                "forward secrecy, disabled by default in current JDKs; enable ECDHE cipher " +
                "suites on the server)",
            handshake.logMessage,
        )
    }

    @Test
    fun `falls back to the formatted message for unexpected parameters`() {
        val expected =
            TlsCompatibility.Handshake("github.com", "443", "TLSv1.3", "TLS_AES_128_GCM_SHA256")
        assertEquals(
            expected,
            TlsCompatibility.handshakeOf(
                " TLSHandshake: github.com:443, TLSv1.3, TLS_AES_128_GCM_SHA256, 1778547583",
                null,
            ),
        )
        assertEquals(
            expected,
            TlsCompatibility.handshakeOf(
                " TLSHandshake: {0}:{1}, {2}, {3}, {4}",
                arrayOf("github.com", "443", "TLSv1.3", "TLS_AES_128_GCM_SHA256", "1778547583"),
            ),
        )
    }

    @Test
    fun `ignores other security events and unreadable records`() {
        assertNull(TlsCompatibility.handshakeOf(null, null))
        assertNull(
            TlsCompatibility.handshakeOf(
                "X509Certificate: Alg:{0}, Serial:{1}, Subject:{2}",
                arrayOf("SHA256withRSA", "01", "CN=db.example.com"),
            ),
        )
        assertNull(
            TlsCompatibility.handshakeOf(
                "SecurityPropertyModification: key:{0}, value:{1}",
                arrayOf("jdk.tls.disabledAlgorithms", "SSLv3"),
            ),
        )
        assertNull(TlsCompatibility.handshakeOf(" TLSHandshake: {0}", arrayOf(null)))
        assertNull(TlsCompatibility.handshakeOf(" TLSHandshake: not a handshake", emptyArray()))
        // The port is not a number: neither the parameters nor the number format can be used.
        assertNull(
            TlsCompatibility.handshakeOf(
                HANDSHAKE_TEMPLATE,
                arrayOf<Any>("github.com", "https", "TLSv1.3", "TLS_AES_128_GCM_SHA256", 1L),
            ),
        )
    }

    companion object {
        /** Message template of the JDK's `TLSHandshake` security event log record. */
        const val HANDSHAKE_TEMPLATE = " TLSHandshake: {0}:{1,number,#}, {2}, {3}, {4,number,#}"
        const val CORRETTO_21_0_6 =
            "SSLv3, TLSv1, TLSv1.1, DTLSv1.0, RC4, DES, MD5withRSA, DH keySize < 1024, " +
                "EC keySize < 224, 3DES_EDE_CBC, anon, NULL, ECDH"
        const val CORRETTO_21_0_13 =
            "$CORRETTO_21_0_6, TLS_RSA_*, rsa_pkcs1_sha1 usage HandshakeSignature, " +
                "ecdsa_sha1 usage HandshakeSignature, dsa_sha1 usage HandshakeSignature"
    }
}
