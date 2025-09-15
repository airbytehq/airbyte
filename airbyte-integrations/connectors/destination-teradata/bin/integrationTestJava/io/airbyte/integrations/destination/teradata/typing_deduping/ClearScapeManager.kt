/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.destination.teradata.envclient.TeradataHttpClient
import io.airbyte.integrations.destination.teradata.envclient.dto.*
import io.airbyte.integrations.destination.teradata.envclient.exception.BaseException
import io.airbyte.integrations.destination.teradata.util.TeradataConstants
import java.net.URISyntaxException
import java.nio.file.Files
import java.nio.file.Paths
import java.util.regex.Pattern
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Manager class responsible for provisioning, starting, and tearing down ClearScape environments
 * using the Teradata Environment API.
 *
 * This class reads configuration from a JSON file, uses the environment configuration to call the
 * Teradata ClearScape HTTP API, and sets up the necessary JDBC parameters for connecting to a
 * Teradata instance.
 *
 * @param configFileName the path to the configuration JSON file.
 */
class ClearScapeManager(private val configFileName: String) {

    private val LOGGER: Logger =
        LoggerFactory.getLogger(AbstractTeradataTypingDedupingTest::class.java)

    /** Configuration object loaded from the JSON file. */
    var configJSON: ObjectNode = loadConfig(configFileName)

    private val ALLOWED_URL_PATTERN: Pattern =
        Pattern.compile("^(https?://)(www\\.)?api.clearscape.teradata\\.com.*")

    /**
     * Validates that the provided URL matches the expected Clearscape Teradata API pattern.
     *
     * @param url the environment URL to validate
     * @return true if the URL is valid, false otherwise
     */
    private fun isValidUrl(url: String): Boolean {
        return ALLOWED_URL_PATTERN.matcher(url).matches()
    }

    /**
     * Creates a new instance of [TeradataHttpClient] using the environment URL from the config.
     *
     * @param config the loaded JSON configuration
     * @return an initialized [TeradataHttpClient] instance
     * @throws URISyntaxException if the environment URL is invalid
     */
    @Throws(URISyntaxException::class)
    private fun getTeradataHttpClient(config: JsonNode): TeradataHttpClient {
        val envUrl = config["env_url"].asText()
        if (isValidUrl(envUrl)) {
            return TeradataHttpClient(envUrl)
        } else {
            throw URISyntaxException(envUrl, "Provide valid environment URL")
        }
    }

    /**
     * Public method to create and start the ClearScape environment instance. Should be called
     * before any operations requiring an active environment.
     */
    fun setup() {
        createAndStartClearScapeInstance()
    }

    /** Public method to stop the clea */
    fun stop() {
        stopClearScapeInstance()
    }

    /**
     * Public method to shut down and delete the ClearScape environment instance. Should be called
     * to clean up resources after usage.
     */
    fun teardown() {
        shutdownAndDestroyClearScapeInstance()
    }

    /**
     * Handles the logic for creating and starting a ClearScape environment instance. If the
     * environment already exists and is stopped, it is started. If it doesn't exist, a new
     * environment is created. Updates the `configJSON` with host/IP and authentication info.
     */
    private fun createAndStartClearScapeInstance() {
        val teradataHttpClient = getTeradataHttpClient(configJSON)
        val name = configJSON["env_name"].asText()
        val token = configJSON["env_token"].asText()

        var response: EnvironmentResponse? = null
        try {
            response = teradataHttpClient.getEnvironment(GetEnvironmentRequest(name), token)
        } catch (be: BaseException) {
            LOGGER.info("Environment $name is not available. ${be.message}")
        }

        if (response == null || response.ip == null) {
            val request =
                CreateEnvironmentRequest(
                    name,
                    configJSON["env_region"].asText(),
                    configJSON["env_password"].asText(),
                )
            response = teradataHttpClient.createEnvironment(request, token).get()
        } else if (response.state == EnvironmentResponse.State.STOPPED) {
            val request = EnvironmentRequest(name, OperationRequest("start"))
            teradataHttpClient.startEnvironment(request, token)
        }

        if (response != null) {
            configJSON.put(JdbcUtils.HOST_KEY, response.ip)
        }

        val authMap =
            ImmutableMap.builder<Any, Any>()
                .put(TeradataConstants.AUTH_TYPE, "TD2")
                .put(JdbcUtils.USERNAME_KEY, configJSON["username"].asText())
                .put(JdbcUtils.PASSWORD_KEY, configJSON["env_password"].asText())
                .build()

        configJSON.set<JsonNode>(TeradataConstants.LOG_MECH, Jsons.jsonNode(authMap))
    }

    /** Handles the logic for stopping a ClearScape environment instance. */
    private fun stopClearScapeInstance() {
        val teradataHttpClient = getTeradataHttpClient(configJSON)
        val name = configJSON["env_name"].asText()
        val token = configJSON["env_token"].asText()

        var response: EnvironmentResponse? = null
        try {
            response = teradataHttpClient.getEnvironment(GetEnvironmentRequest(name), token)
        } catch (be: BaseException) {
            LOGGER.info("Environment $name is not available. ${be.message}")
        }
        if (
            response != null &&
                response.ip != null &&
                response.state == EnvironmentResponse.State.RUNNING
        ) {
            val request = EnvironmentRequest(name, OperationRequest("stop"))
            teradataHttpClient.stopEnvironment(request, token)
        }
    }

    /**
     * Handles the logic for shutting down and deleting a ClearScape environment instance. Logs a
     * warning if the environment is not available.
     */
    private fun shutdownAndDestroyClearScapeInstance() {
        try {
            val teradataHttpClient = getTeradataHttpClient(configJSON)
            val token = configJSON["env_token"].asText()
            val request = DeleteEnvironmentRequest(configJSON["env_name"].asText())
            teradataHttpClient.deleteEnvironment(request, token).get()
        } catch (be: BaseException) {
            LOGGER.info(
                "Environment ${configJSON["env_name"].asText()} is not available. Error - ${be.message}"
            )
        }
    }

    /**
     * Loads a JSON configuration file from the provided file path.
     *
     * @param fileName the path to the config file
     * @return the parsed [ObjectNode] representing the configuration
     * @throws RuntimeException if the file is missing or unreadable
     */
    private fun loadConfig(fileName: String): ObjectNode {
        return try {
            val configPath = Paths.get(fileName)
            if (Files.exists(configPath)) {
                Jsons.deserialize(Files.readString(configPath)) as ObjectNode
            } else {
                throw IllegalArgumentException("Config file not found: $fileName")
            }
        } catch (e: Exception) {
            throw RuntimeException("Failed to load configuration from file: $fileName", e)
        }
    }
}
