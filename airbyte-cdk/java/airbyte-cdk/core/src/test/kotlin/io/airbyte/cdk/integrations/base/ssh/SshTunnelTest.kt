/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.ssh

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.commons.json.Jsons
import java.nio.charset.StandardCharsets
import java.security.*
import java.util.*
import org.apache.sshd.client.SshClient
import org.apache.sshd.client.session.ClientSession
import org.apache.sshd.common.util.security.SecurityUtils
import org.apache.sshd.common.util.security.eddsa.EdDSASecurityProviderRegistrar
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SshTunnelTest {
    /**
     * This test verifies that OpenSsh correctly replaces values in connector configuration in a
     * spec with host/port config and in a spec with endpoint URL config
     *
     * @param configString
     * @throws Exception
     */
    @ParameterizedTest
    @ValueSource(strings = [HOST_PORT_CONFIG, URL_CONFIG_WITH_PORT, URL_CONFIG_NO_PORT])
    @Throws(Exception::class)
    fun testConfigInTunnel(configString: String) {
        val config = ObjectMapper().readTree(String.format(configString, SSH_RSA_PRIVATE_KEY))
        val endPointURL = Jsons.getStringOrNull(config, "endpoint")
        val sshTunnel: SshTunnel =
            object :
                SshTunnel(
                    config,
                    if (endPointURL == null) Arrays.asList(*arrayOf("host")) else null,
                    if (endPointURL == null) Arrays.asList(*arrayOf("port")) else null,
                    if (endPointURL == null) null else "endpoint",
                    endPointURL,
                    TunnelMethod.SSH_KEY_AUTH,
                    "faketunnel.com",
                    22,
                    "tunnelUser",
                    SSH_RSA_PRIVATE_KEY,
                    "tunnelUserPassword",
                    if (endPointURL == null) "fakeHost.com" else null,
                    if (endPointURL == null) 5432 else 0
                ) {
                public override fun openTunnel(client: SshClient): ClientSession? {
                    tunnelLocalPort = 8080
                    return null // Prevent tunnel from attempting to connect
                }
            }

        val configInTunnel = sshTunnel.configInTunnel
        if (endPointURL == null) {
            Assertions.assertTrue(configInTunnel.has("port"))
            Assertions.assertTrue(configInTunnel.has("host"))
            Assertions.assertFalse(configInTunnel.has("endpoint"))
            Assertions.assertEquals(8080, configInTunnel["port"].asInt())
            Assertions.assertEquals("127.0.0.1", configInTunnel["host"].asText())
        } else {
            Assertions.assertFalse(configInTunnel.has("port"))
            Assertions.assertFalse(configInTunnel.has("host"))
            Assertions.assertTrue(configInTunnel.has("endpoint"))
            Assertions.assertEquals(
                "http://127.0.0.1:8080/service",
                configInTunnel["endpoint"].asText()
            )
        }
    }

    /**
     * This test verifies that SshTunnel correctly extracts private key pairs from keys formatted as
     * EdDSA and OpenSSH
     *
     * @param privateKey
     * @throws Exception
     */
    @ParameterizedTest
    @ValueSource(strings = [SSH_ED25519_PRIVATE_KEY, SSH_RSA_PRIVATE_KEY])
    @Throws(Exception::class)
    fun getKeyPair(privateKey: String?) {
        val config = ObjectMapper().readTree(String.format(HOST_PORT_CONFIG, privateKey))
        val sshTunnel: SshTunnel =
            object :
                SshTunnel(
                    config,
                    Arrays.asList(*arrayOf("host")),
                    Arrays.asList(*arrayOf("port")),
                    null,
                    null,
                    TunnelMethod.SSH_KEY_AUTH,
                    "faketunnel.com",
                    22,
                    "tunnelUser",
                    privateKey,
                    "tunnelUserPassword",
                    "fakeHost.com",
                    5432
                ) {
                public override fun openTunnel(client: SshClient): ClientSession? {
                    return null // Prevent tunnel from attempting to connect
                }
            }

        val authKeyPair = sshTunnel.privateKeyPair
        Assertions.assertNotNull(
            authKeyPair
        ) // actually, all is good if there is no exception on previous line
    }

    /**
     * This test verifies that 'net.i2p.crypto:eddsa' is present and EdDSA is supported. If
     * net.i2p.crypto:eddsa will be removed from project, then will be thrown: generator not
     * correctly initialized
     *
     * @throws Exception
     */
    @Test
    @Throws(Exception::class)
    fun edDsaIsSupported() {
        val keygen = SecurityUtils.getKeyPairGenerator("EdDSA")
        val message = "hello world"
        val keyPair = keygen.generateKeyPair()

        val signedMessage = sign(keyPair.private, message)

        Assertions.assertTrue(EdDSASecurityProviderRegistrar().isSupported)
        Assertions.assertTrue(verify(keyPair.public, signedMessage, message))
    }

    @Throws(Exception::class)
    private fun sign(privateKey: PrivateKey, message: String): ByteArray {
        val signature = SecurityUtils.getSignature("NONEwithEdDSA")
        signature.initSign(privateKey)

        signature.update(message.toByteArray(StandardCharsets.UTF_8))

        return signature.sign()
    }

    @Throws(Exception::class)
    private fun verify(publicKey: PublicKey, signed: ByteArray, message: String): Boolean {
        val signature = SecurityUtils.getSignature("NONEwithEdDSA")
        signature.initVerify(publicKey)

        signature.update(message.toByteArray(StandardCharsets.UTF_8))

        return signature.verify(signed)
    }

    companion object {
        private const val SSH_ED25519_PRIVATE_KEY =
            ("-----BEGIN OPENSSH PRIVATE KEY-----\\n" +
                "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW\\n" +
                "QyNTUxOQAAACDbBP+5jmEtjh1JvhzVQsvvTC2IQrX6P68XzrV7ZbnGsQAAAKBgtw9/YLcP\\n" +
                "fwAAAAtzc2gtZWQyNTUxOQAAACDbBP+5jmEtjh1JvhzVQsvvTC2IQrX6P68XzrV7ZbnGsQ\\n" +
                "AAAEAaKYn22N1O78HfdG22C7hcG2HiezKMzlq4JTdgYG1DstsE/7mOYS2OHUm+HNVCy+9M\\n" +
                "LYhCtfo/rxfOtXtlucaxAAAAHHRmbG9yZXNfZHQwMUB0ZmxvcmVzX2R0MDEtUEMB\\n" +
                "-----END OPENSSH PRIVATE KEY-----")
        private const val SSH_RSA_PRIVATE_KEY =
            ("-----BEGIN OPENSSH PRIVATE KEY-----\\n" +
                "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn\\n" +
                "NhAAAAAwEAAQAAAYEAuFjfTMS6BrgoxaQe9i83y6CdGH3xJIwc1Wy+11ibWAFcQ6khX/x0\\n" +
                "M+JnJaSCs/hxiDE4afHscP3HzVQC699IgKwyAPaG0ZG+bLhxWAm4E79P7Yssj7imhTqr0A\\n" +
                "DZDO23CCOagHvfdg1svnBhk1ih14GMGKRFCS27CLgholIOeogOyH7b3Jaqy9LtICiE054e\\n" +
                "jwdaZdwWU08kxMO4ItdxNasCPC5uQiaXIzWFysG0mLk7WWc8WyuQHneQFl3Qu6p/rWJz4i\\n" +
                "seea5CBL5s1DIyCyo/jgN5/oOWOciPUl49mDLleCzYTDnWqX43NK9A87unNeuA95Fk9akH\\n" +
                "8QH4hKBCzpHhsh4U3Ys/l9Q5NmnyBrtFWBY2n13ZftNA/Ms+Hsh6V3eyJW0rIFY2/UM4XA\\n" +
                "YyD6MEOlvFAQjxC6EbqfkrC6FQgH3I2wAtIDqEk2j79vfIIDdzp8otWjIQsApX55j+kKio\\n" +
                "sY8YTXb9sLWuEdpSd/AN3iQ8HwIceyTulaKn7rTBAAAFkMwDTyPMA08jAAAAB3NzaC1yc2\\n" +
                "EAAAGBALhY30zEuga4KMWkHvYvN8ugnRh98SSMHNVsvtdYm1gBXEOpIV/8dDPiZyWkgrP4\\n" +
                "cYgxOGnx7HD9x81UAuvfSICsMgD2htGRvmy4cVgJuBO/T+2LLI+4poU6q9AA2Qzttwgjmo\\n" +
                "B733YNbL5wYZNYodeBjBikRQktuwi4IaJSDnqIDsh+29yWqsvS7SAohNOeHo8HWmXcFlNP\\n" +
                "JMTDuCLXcTWrAjwubkImlyM1hcrBtJi5O1lnPFsrkB53kBZd0Luqf61ic+IrHnmuQgS+bN\\n" +
                "QyMgsqP44Def6DljnIj1JePZgy5Xgs2Ew51ql+NzSvQPO7pzXrgPeRZPWpB/EB+ISgQs6R\\n" +
                "4bIeFN2LP5fUOTZp8ga7RVgWNp9d2X7TQPzLPh7Ield3siVtKyBWNv1DOFwGMg+jBDpbxQ\\n" +
                "EI8QuhG6n5KwuhUIB9yNsALSA6hJNo+/b3yCA3c6fKLVoyELAKV+eY/pCoqLGPGE12/bC1\\n" +
                "rhHaUnfwDd4kPB8CHHsk7pWip+60wQAAAAMBAAEAAAGAXw+dHpY3o21lwP0v5h1VNVD+kX\\n" +
                "moVwNVfw0ToDKV8JzK+i0GA9xIA9VVAUlDCREtYmCXSbKyDVYgqRYQZ5d9aLTjGDIINZtl\\n" +
                "SeUWtaJVZQF7cvAYq4g5fmxR2vIE+zC9+Jl7e5PlGJg1okKLXpMO6fVoy/AxlVkaoJVq6q\\n" +
                "xLwQ3WKbeZIrgjHPYIx1N9oy5fbbwJ9oq2jIE8YabXlkfonhcwEN6UhtIlj8dy1apruXGT\\n" +
                "VDfzHMRrDfrzt0TrdUqmqgo/istP89sggtkJ8uuPtkBFHTjao8MiBsshy1iDVbIno9gDbJ\\n" +
                "JgYyunmSgEjEZpp09+mkgwfZO3/RDLRPF1SRAGBNy27CH8/bh9gAVRhAPi0GLclNi292Ya\\n" +
                "NrGvjMcRlYAsWL3mZ9aTbv0j7Qi8qdWth+rZ+tBmNToUVVl5iLxifgo0kjiXAehZB1LaQV\\n" +
                "yuMXlXOGmt9V2/DPACA9getQJQONxrLAcgHdjMiuwD8r7d+m/kE4+cOTakOlzrfrwBAAAA\\n" +
                "wQCVTQTvuyBW3JemMPtRLifQqdwMGRPokm5nTn+JSJQvg+dNpL7hC0k3IesKs63gxuuHoq\\n" +
                "4q1xkMmCMvihT8oVlxrezEjsO/QMCxe6Sr9eMfHAjrdPeHsPaf9oOgG9vEEH9dEilHpnlb\\n" +
                "97Vyl9EHm1iahONM1gWdXkPjIfnQzYPvSLZPtBBSI0XBjCTifMnCRgd3s2bdm7kh+7XA+C\\n" +
                "rX62WfPIJKL+OhMIf+ED4HBJTd/vU34Vk73yvqHzqel0ZQnRoAAADBAOGSm6TNBptV7S5P\\n" +
                "wT3BhGYSm35/7nCFTilyfy5/8EUmifUFittRIvgDoXBWeZEwvqIiQ55iX9mYmNmb0KbPCw\\n" +
                "cqN/BtXWItAvyTDZ6PeI2m2aUj+rW2R3ZXEsBjgaNRtbPyMKQ69xtKRvHtNZNfgjpRQ4is\\n" +
                "lbufhAK1YbUxrlfKaBGOcGyR7DNmUUUN6nptQbpOr1HQc5DOH17HIDnRPs44HIws3/apww\\n" +
                "RBIjjy6GQNfJ/Ge8N4pxGoLl1qKO8xoQAAAMEA0Tat/E5mSsgjCgmFja/jOZJcrzZHwrPT\\n" +
                "3NEbuAMQ/L3atKEINypmpJfjIAvNljKJwSUDMEWvs8qj8cSGCrtkcAv1YSm697TL2oC9HU\\n" +
                "CFoOJAkH1X2CGTgHlR9it3j4aRJ3dXdL2k7aeoGXObfRWqBNPj0LOOZs64RA6scGAzo6MR\\n" +
                "5WlcOxfV1wZuaM0fOd+PBmIlFEE7Uf6AY/UahBAxaFV2+twgK9GCDcu1t4Ye9wZ9kZ4Nal\\n" +
                "0fkKD4uN4DRO8hAAAAFm10dWhhaUBrYnAxLWxocC1hMTQ1MzMBAgME\\n" +
                "-----END OPENSSH PRIVATE KEY-----")
        private const val HOST_PORT_CONFIG =
            ("{\"ssl\":true,\"host\":\"fakehost.com\",\"port\":5432,\"schema\":\"public\",\"database\":\"postgres\",\"password\":\"<dummyPassword>\",\"username\":\"postgres\",\"tunnel_method\":{\"ssh_key\":\"" +
                "%s" +
                "\",\"tunnel_host\":\"faketunnel.com\",\"tunnel_port\":22,\"tunnel_user\":\"ec2-user\",\"tunnel_method\":\"SSH_KEY_AUTH\"}}")

        private const val URL_CONFIG_WITH_PORT =
            ("{\"ssl\":true,\"endpoint\":\"http://fakehost.com:9090/service\",\"password\":\"<dummyPassword>\",\"username\":\"restuser\",\"tunnel_method\":{\"ssh_key\":\"" +
                "%s" +
                "\",\"tunnel_host\":\"faketunnel.com\",\"tunnel_port\":22,\"tunnel_user\":\"ec2-user\",\"tunnel_method\":\"SSH_KEY_AUTH\"}}")

        private const val URL_CONFIG_NO_PORT =
            ("{\"ssl\":true,\"endpoint\":\"http://fakehost.com/service\",\"password\":\"<dummyPassword>\",\"username\":\"restuser\",\"tunnel_method\":{\"ssh_key\":\"" +
                "%s" +
                "\",\"tunnel_host\":\"faketunnel.com\",\"tunnel_port\":22,\"tunnel_user\":\"ec2-user\",\"tunnel_method\":\"SSH_KEY_AUTH\"}}")
    }
}
