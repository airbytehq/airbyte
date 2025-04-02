/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.destination.teradata.envclient.TeradataHttpClient
import io.airbyte.integrations.destination.teradata.envclient.dto.CreateEnvironmentRequest
import io.airbyte.integrations.destination.teradata.envclient.dto.DeleteEnvironmentRequest
import io.airbyte.integrations.destination.teradata.envclient.dto.EnvironmentRequest
import io.airbyte.integrations.destination.teradata.envclient.dto.EnvironmentResponse
import io.airbyte.integrations.destination.teradata.envclient.dto.GetEnvironmentRequest
import io.airbyte.integrations.destination.teradata.envclient.dto.OperationRequest
import io.airbyte.integrations.destination.teradata.envclient.exception.BaseException
import io.airbyte.integrations.destination.teradata.util.TeradataConstants
import java.net.URISyntaxException
import java.nio.file.Files
import java.nio.file.Paths
import java.util.regex.Pattern
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class TeradataBaseTest() {

    fun init(filePath: String) {
        configJson = Jsons.deserialize(Files.readString(Paths.get(filePath)))
        val teradataHttpClient =
            getTeradataHttpClient(
                configJson,
            )
        val name = configJson["env_name"].asText()
        val token = configJson["env_token"].asText()
        val getRequest = GetEnvironmentRequest(name)
        var response: EnvironmentResponse? = null
        try {
            response = teradataHttpClient.getEnvironment(getRequest, token)
        } catch (be: BaseException) {
            LOGGER.info("Environemnt " + name + " is not available. " + be.message)
        }
        if (response == null || response.ip == null) {
            val request =
                CreateEnvironmentRequest(
                    name,
                    configJson["env_region"].asText(),
                    configJson["env_password"].asText(),
                )
            response = teradataHttpClient.createEnvironment(request, token).get()
            LOGGER.info(
                "Environemnt {} is created successfully ",
                configJson["env_name"].asText(),
            )
        } else if (response.state == EnvironmentResponse.State.STOPPED) {
            val request = EnvironmentRequest(name, OperationRequest("start"))
            teradataHttpClient.startEnvironment(request, token)
        }
        if (response != null) {
            (configJson as ObjectNode).put(JdbcUtils.HOST_KEY, response.ip)
        }
        val authMap =
            ImmutableMap.builder<Any, Any>()
                .put(TeradataConstants.AUTH_TYPE, "TD2")
                .put(JdbcUtils.USERNAME_KEY, configJson.get("username").asText())
                .put(JdbcUtils.PASSWORD_KEY, configJson.get("env_password").asText())
                .build()
        (configJson as ObjectNode).set<JsonNode>(
            TeradataConstants.LOG_MECH,
            Jsons.jsonNode(authMap),
        )
    }

    fun clean() {
        try {
            val teradataHttpClient =
                getTeradataHttpClient(
                    configJson,
                )
            val token = configJson["env_token"].asText()
            val request =
                DeleteEnvironmentRequest(
                    configJson["env_name"].asText(),
                )
            teradataHttpClient.deleteEnvironment(request, token)
            LOGGER.info(
                "Environemnt {} is deleted successfully ",
                configJson["env_name"].asText(),
            )
        } catch (be: BaseException) {
            LOGGER.info(
                "Environemnt " +
                    configJson["env_name"].asText() +
                    " is not available. " +
                    be.message
            )
        }
    }

    private val ALLOWED_URL_PATTERN: Pattern =
        Pattern.compile("^(https?://)(www\\.)?api.clearscape.teradata\\.com.*")

    private fun isValidUrl(url: String): Boolean {
        return ALLOWED_URL_PATTERN.matcher(url).matches()
    }

    @Throws(URISyntaxException::class)
    private fun getTeradataHttpClient(config: JsonNode): TeradataHttpClient {
        val envUrl = config["env_url"].asText()
        if (isValidUrl(envUrl)) {
            return TeradataHttpClient(envUrl)
        } else {
            LOGGER.error("Invalid or untrusted URL")
            throw URISyntaxException(envUrl, "Provide valid environment URL")
        }
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(
                TeradataBaseTest::class.java,
            )
        lateinit var configJson: JsonNode
    }
}
