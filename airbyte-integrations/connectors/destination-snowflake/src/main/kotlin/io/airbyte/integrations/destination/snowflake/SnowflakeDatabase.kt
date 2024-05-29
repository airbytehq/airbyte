/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.commons.json.Jsons.deserialize
import java.io.IOException
import java.io.PrintWriter
import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpRequest.BodyPublishers
import java.net.http.HttpResponse
import java.nio.charset.StandardCharsets
import java.time.Duration
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.stream.Collectors
import javax.sql.DataSource
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** SnowflakeDatabase contains helpers to create connections to and run queries on Snowflake. */
object SnowflakeDatabase {
    private val LOGGER: Logger = LoggerFactory.getLogger(SnowflakeDatabase::class.java)
    private const val PAUSE_BETWEEN_TOKEN_REFRESH_MIN =
        7 // snowflake access token TTL is 10min and can't be modified

    private val NETWORK_TIMEOUT: Duration = Duration.ofMinutes(1)
    private val nameTransformer = SnowflakeSQLNameTransformer()
    private const val DRIVER_CLASS_NAME = "net.snowflake.client.jdbc.SnowflakeDriver"

    private const val REFRESH_TOKEN_URL = "https://%s/oauth/token-request"
    private val httpClient: HttpClient =
        HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .connectTimeout(Duration.ofSeconds(10))
            .build()
    const val PRIVATE_KEY_FILE_NAME: String = "rsa_key.p8"
    const val PRIVATE_KEY_FIELD_NAME: String = "private_key"
    const val PRIVATE_KEY_PASSWORD: String = "private_key_password"
    private const val CONNECTION_STRING_IDENTIFIER_KEY = "application"
    private const val CONNECTION_STRING_IDENTIFIER_VAL = "Airbyte_Connector"

    @JvmStatic
    fun createDataSource(config: JsonNode, airbyteEnvironment: String?): HikariDataSource {
        val dataSource = HikariDataSource()

        val jdbcUrl =
            StringBuilder(
                String.format("jdbc:snowflake://%s/?", config[JdbcUtils.HOST_KEY].asText())
            )
        val username = config[JdbcUtils.USERNAME_KEY].asText()

        val properties = Properties()

        val credentials = config["credentials"]
        if (
            credentials != null &&
                credentials.has("auth_type") &&
                "OAuth2.0" == credentials["auth_type"].asText()
        ) {
            LOGGER.debug("OAuth login mode is used")
            // OAuth login option is selected on UI
            val accessToken: String
            try {
                // accessToken is only valid for 10 minutes. So we need to get a new one before
                // processing new
                // stream
                accessToken =
                    getAccessTokenUsingRefreshToken(
                        config[JdbcUtils.HOST_KEY].asText(),
                        credentials["client_id"].asText(),
                        credentials["client_secret"].asText(),
                        credentials["refresh_token"].asText()
                    )
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
            properties[CONNECTION_STRING_IDENTIFIER_KEY] = CONNECTION_STRING_IDENTIFIER_VAL
            properties["client_id"] = credentials["client_id"].asText()
            properties["client_secret"] = credentials["client_secret"].asText()
            properties["refresh_token"] = credentials["refresh_token"].asText()
            properties[JdbcUtils.HOST_KEY] = config[JdbcUtils.HOST_KEY].asText()
            properties["authenticator"] = "oauth"
            properties["token"] = accessToken
            // the username is required for DBT normalization in OAuth connection
            properties[JdbcUtils.USERNAME_KEY] = username

            // thread to keep the refresh token up to date
            SnowflakeDestination.SCHEDULED_EXECUTOR_SERVICE.scheduleAtFixedRate(
                getRefreshTokenTask(dataSource),
                PAUSE_BETWEEN_TOKEN_REFRESH_MIN.toLong(),
                PAUSE_BETWEEN_TOKEN_REFRESH_MIN.toLong(),
                TimeUnit.MINUTES
            )
        } else if (credentials != null && credentials.has(JdbcUtils.PASSWORD_KEY)) {
            LOGGER.debug("User/password login mode is used")
            // Username and pass login option is selected on UI
            dataSource.username = username
            dataSource.password = credentials[JdbcUtils.PASSWORD_KEY].asText()
        } else if (credentials != null && credentials.has(PRIVATE_KEY_FIELD_NAME)) {
            LOGGER.debug("Login mode with key pair is used")
            dataSource.username = username
            val privateKeyValue = credentials[PRIVATE_KEY_FIELD_NAME].asText()
            createPrivateKeyFile(PRIVATE_KEY_FILE_NAME, privateKeyValue)
            properties["private_key_file"] = PRIVATE_KEY_FILE_NAME
            if (credentials.has(PRIVATE_KEY_PASSWORD)) {
                properties["private_key_file_pwd"] = credentials[PRIVATE_KEY_PASSWORD].asText()
            }
        } else {
            LOGGER.warn(
                "Obsolete User/password login mode is used. Please re-create a connection to use the latest connector's version"
            )
            // case to keep the backward compatibility
            dataSource.username = username
            dataSource.password = config[JdbcUtils.PASSWORD_KEY].asText()
        }

        properties["warehouse"] = config["warehouse"].asText()
        properties[JdbcUtils.DATABASE_KEY] = config[JdbcUtils.DATABASE_KEY].asText()
        properties["role"] = config["role"].asText()
        properties[JdbcUtils.SCHEMA_KEY] =
            nameTransformer.getIdentifier(config[JdbcUtils.SCHEMA_KEY].asText())

        properties["networkTimeout"] = Math.toIntExact(NETWORK_TIMEOUT.toSeconds())
        // allows queries to contain any number of statements.
        properties["MULTI_STATEMENT_COUNT"] = 0

        // https://docs.snowflake.com/en/user-guide/jdbc-parameters.html#application
        // identify airbyte traffic to snowflake to enable partnership & optimization opportunities
        properties["application"] = airbyteEnvironment // see envs in OssCloudEnvVarConsts class
        // Needed for JDK17 - see
        // https://stackoverflow.com/questions/67409650/snowflake-jdbc-driver-internal-error-fail-to-retrieve-row-count-for-first-arrow
        properties["JDBC_QUERY_RESULT_FORMAT"] = "JSON"

        // https://docs.snowflake.com/sql-reference/parameters#abort-detached-query
        // If the connector crashes, snowflake should abort in-flight queries.
        properties["ABORT_DETACHED_QUERY"] = "true"

        // https://docs.snowflake.com/en/user-guide/jdbc-configure.html#jdbc-driver-connection-string
        if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
            jdbcUrl.append(config[JdbcUtils.JDBC_URL_PARAMS_KEY].asText())
        }

        dataSource.driverClassName = DRIVER_CLASS_NAME
        dataSource.jdbcUrl = jdbcUrl.toString()
        dataSource.dataSourceProperties = properties
        return dataSource
    }

    private fun createPrivateKeyFile(fileName: String, fileValue: String) {
        try {
            PrintWriter(fileName, StandardCharsets.UTF_8).use { out -> out.print(fileValue) }
        } catch (e: IOException) {
            throw RuntimeException("Failed to create file for private key")
        }
    }

    @Throws(IOException::class)
    private fun getAccessTokenUsingRefreshToken(
        hostName: String,
        clientId: String,
        clientSecret: String,
        refreshCode: String
    ): String {
        val refreshTokenUri = String.format(REFRESH_TOKEN_URL, hostName)
        val requestBody: MutableMap<String, String> = HashMap()
        requestBody["grant_type"] = "refresh_token"
        requestBody["refresh_token"] = refreshCode

        try {
            val bodyPublisher =
                BodyPublishers.ofString(
                    requestBody.keys
                        .stream()
                        .map { key: String ->
                            key + "=" + URLEncoder.encode(requestBody[key], StandardCharsets.UTF_8)
                        }
                        .collect(Collectors.joining("&"))
                )

            val authorization =
                Base64.getEncoder()
                    .encode("$clientId:$clientSecret".toByteArray(StandardCharsets.UTF_8))

            val request =
                HttpRequest.newBuilder()
                    .POST(bodyPublisher)
                    .uri(URI.create(refreshTokenUri))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .header("Accept", "application/json")
                    .header(
                        "Authorization",
                        "Basic " + String(authorization, StandardCharsets.UTF_8)
                    )
                    .build()

            val response = httpClient.send(request, HttpResponse.BodyHandlers.ofString())

            val jsonResponse = deserialize(response.body())
            if (jsonResponse.has("access_token")) {
                return jsonResponse["access_token"].asText()
            } else {
                throw RuntimeException(
                    "Failed to obtain accessToken using refresh token. $jsonResponse"
                )
            }
        } catch (e: InterruptedException) {
            throw IOException("Failed to refreshToken", e)
        }
    }

    @JvmStatic
    fun getDatabase(dataSource: DataSource): JdbcDatabase {
        return DefaultJdbcDatabase(dataSource, SnowflakeSourceOperations())
    }

    private fun getRefreshTokenTask(dataSource: HikariDataSource): Runnable {
        return Runnable {
            LOGGER.info("Refresh token process started")
            val props = dataSource.dataSourceProperties
            try {
                val token =
                    getAccessTokenUsingRefreshToken(
                        props.getProperty(JdbcUtils.HOST_KEY),
                        props.getProperty("client_id"),
                        props.getProperty("client_secret"),
                        props.getProperty("refresh_token")
                    )
                props.setProperty("token", token)
                dataSource.dataSourceProperties = props

                LOGGER.info("New refresh token has been obtained")
            } catch (e: IOException) {
                LOGGER.error("Failed to obtain a fresh accessToken:$e")
            }
        }
    }
}
