/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import com.fasterxml.jackson.databind.JsonNode
import java.io.*
import java.nio.charset.StandardCharsets
import java.util.concurrent.TimeUnit
import org.apache.commons.lang3.RandomStringUtils

object PostgresSslConnectionUtils {
    private const val CA_CERTIFICATE = "ca.crt"
    private const val CLIENT_CERTIFICATE = "client.crt"
    private const val CLIENT_KEY = "client.key"
    private const val CLIENT_ENCRYPTED_KEY = "client.pk8"

    const val PARAM_MODE: String = "mode"
    const val PARAM_SSL: String = "ssl"
    const val PARAM_SSL_MODE: String = "ssl_mode"
    const val PARAM_SSLMODE: String = "sslmode"
    const val PARAM_CLIENT_KEY_PASSWORD: String = "client_key_password"
    const val PARAM_CA_CERTIFICATE: String = "ca_certificate"
    const val PARAM_CLIENT_CERTIFICATE: String = "client_certificate"
    const val PARAM_CLIENT_KEY: String = "client_key"

    const val VERIFY_CA: String = "verify-ca"
    const val VERIFY_FULL: String = "verify-full"
    const val DISABLE: String = "disable"
    const val TRUE_STRING_VALUE: String = "true"
    const val ENCRYPT_FILE_NAME: String = "encrypt"
    const val FACTORY_VALUE: String = "org.postgresql.ssl.DefaultJavaSSLFactory"

    @JvmStatic
    fun obtainConnectionOptions(encryption: JsonNode): Map<String, String> {
        val additionalParameters: MutableMap<String, String> = HashMap()
        if (!encryption.isNull) {
            val method = encryption[PARAM_MODE].asText()
            val keyStorePassword = checkOrCreatePassword(encryption)
            when (method) {
                VERIFY_CA -> {
                    additionalParameters.putAll(
                        obtainConnectionCaOptions(encryption, method, keyStorePassword)
                    )
                }
                VERIFY_FULL -> {
                    additionalParameters.putAll(
                        obtainConnectionFullOptions(encryption, method, keyStorePassword)
                    )
                }
                else -> {
                    additionalParameters[PARAM_SSL] = TRUE_STRING_VALUE
                    additionalParameters[PARAM_SSLMODE] = method
                }
            }
        }
        return additionalParameters
    }

    private fun checkOrCreatePassword(encryption: JsonNode): String {
        val sslPassword =
            if (encryption.has(PARAM_CLIENT_KEY_PASSWORD))
                encryption[PARAM_CLIENT_KEY_PASSWORD].asText()
            else ""
        var keyStorePassword = RandomStringUtils.insecure().nextAlphanumeric(10)
        if (sslPassword.isEmpty()) {
            val file = File(ENCRYPT_FILE_NAME)
            if (file.exists()) {
                keyStorePassword = readFile(file)
            } else {
                createCertificateFile(ENCRYPT_FILE_NAME, keyStorePassword)
            }
        } else {
            keyStorePassword = sslPassword
        }
        return keyStorePassword
    }

    private fun readFile(file: File): String {
        try {
            val reader = BufferedReader(FileReader(file, StandardCharsets.UTF_8))
            val currentLine = reader.readLine()
            reader.close()
            return currentLine
        } catch (e: IOException) {
            throw RuntimeException("Failed to read file with encryption")
        }
    }

    private fun obtainConnectionFullOptions(
        encryption: JsonNode,
        method: String,
        clientKeyPassword: String
    ): Map<String, String> {
        val additionalParameters: MutableMap<String, String> = HashMap()
        try {
            convertAndImportFullCertificate(
                encryption[PARAM_CA_CERTIFICATE].asText(),
                encryption[PARAM_CLIENT_CERTIFICATE].asText(),
                encryption[PARAM_CLIENT_KEY].asText(),
                clientKeyPassword
            )
        } catch (e: IOException) {
            throw RuntimeException("Failed to import certificate into Java Keystore")
        } catch (e: InterruptedException) {
            throw RuntimeException("Failed to import certificate into Java Keystore")
        }
        additionalParameters["ssl"] = TRUE_STRING_VALUE
        additionalParameters["sslmode"] = method
        additionalParameters["sslrootcert"] = CA_CERTIFICATE
        additionalParameters["sslcert"] = CLIENT_CERTIFICATE
        additionalParameters["sslkey"] = CLIENT_ENCRYPTED_KEY
        additionalParameters["sslfactory"] = FACTORY_VALUE
        return additionalParameters
    }

    private fun obtainConnectionCaOptions(
        encryption: JsonNode,
        method: String,
        clientKeyPassword: String
    ): Map<String, String> {
        val additionalParameters: MutableMap<String, String> = HashMap()
        try {
            convertAndImportCaCertificate(
                encryption[PARAM_CA_CERTIFICATE].asText(),
                clientKeyPassword
            )
        } catch (e: IOException) {
            throw RuntimeException("Failed to import certificate into Java Keystore")
        } catch (e: InterruptedException) {
            throw RuntimeException("Failed to import certificate into Java Keystore")
        }
        additionalParameters["ssl"] = TRUE_STRING_VALUE
        additionalParameters["sslmode"] = method
        additionalParameters["sslrootcert"] = CA_CERTIFICATE
        additionalParameters["sslfactory"] = FACTORY_VALUE
        return additionalParameters
    }

    @Throws(IOException::class, InterruptedException::class)
    private fun convertAndImportFullCertificate(
        caCertificate: String,
        clientCertificate: String,
        clientKey: String,
        clientKeyPassword: String
    ) {
        val run = Runtime.getRuntime()
        createCaCertificate(caCertificate, clientKeyPassword, run)
        createCertificateFile(CLIENT_CERTIFICATE, clientCertificate)
        createCertificateFile(CLIENT_KEY, clientKey)
        // add client certificate to the custom keystore
        runProcess(
            "keytool -alias client-certificate -keystore customkeystore" +
                " -import -file " +
                CLIENT_CERTIFICATE +
                " -storepass " +
                clientKeyPassword +
                " -noprompt",
            run
        )
        // convert client.key to client.pk8 based on the documentation
        runProcess(
            "openssl pkcs8 -topk8 -inform PEM -in " +
                CLIENT_KEY +
                " -outform DER -out " +
                CLIENT_ENCRYPTED_KEY +
                " -nocrypt",
            run
        )
        runProcess("rm " + CLIENT_KEY, run)

        updateTrustStoreSystemProperty(clientKeyPassword)
    }

    @Throws(IOException::class, InterruptedException::class)
    private fun convertAndImportCaCertificate(caCertificate: String, clientKeyPassword: String) {
        val run = Runtime.getRuntime()
        createCaCertificate(caCertificate, clientKeyPassword, run)
        updateTrustStoreSystemProperty(clientKeyPassword)
    }

    @Throws(IOException::class, InterruptedException::class)
    private fun createCaCertificate(
        caCertificate: String,
        clientKeyPassword: String,
        run: Runtime
    ) {
        createCertificateFile(CA_CERTIFICATE, caCertificate)
        // add CA certificate to the custom keystore
        runProcess(
            "keytool -import -alias rds-root -keystore customkeystore" +
                " -file " +
                CA_CERTIFICATE +
                " -storepass " +
                clientKeyPassword +
                " -noprompt",
            run
        )
    }

    private fun updateTrustStoreSystemProperty(clientKeyPassword: String) {
        val result = System.getProperty("user.dir") + "/customkeystore"
        System.setProperty("javax.net.ssl.trustStore", result)
        System.setProperty("javax.net.ssl.trustStorePassword", clientKeyPassword)
    }

    @Throws(IOException::class)
    private fun createCertificateFile(fileName: String, fileValue: String) {
        PrintWriter(fileName, StandardCharsets.UTF_8).use { out -> out.print(fileValue) }
    }

    @Throws(IOException::class, InterruptedException::class)
    private fun runProcess(cmd: String, run: Runtime) {
        @Suppress("deprecation") val pr = run.exec(cmd)
        if (!pr.waitFor(30, TimeUnit.SECONDS)) {
            pr.destroy()
            throw RuntimeException("Timeout while executing: $cmd")
        }
    }
}
