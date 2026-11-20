/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import org.junit.jupiter.api.Assertions.assertEquals
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

    companion object {
        const val CORRETTO_21_0_6 =
            "SSLv3, TLSv1, TLSv1.1, DTLSv1.0, RC4, DES, MD5withRSA, DH keySize < 1024, " +
                "EC keySize < 224, 3DES_EDE_CBC, anon, NULL, ECDH"
        const val CORRETTO_21_0_13 =
            "$CORRETTO_21_0_6, TLS_RSA_*, rsa_pkcs1_sha1 usage HandshakeSignature, " +
                "ecdsa_sha1 usage HandshakeSignature, dsa_sha1 usage HandshakeSignature"
    }
}
