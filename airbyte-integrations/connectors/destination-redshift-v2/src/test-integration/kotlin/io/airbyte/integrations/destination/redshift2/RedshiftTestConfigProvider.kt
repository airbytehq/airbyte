/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths

private val log = KotlinLogging.logger {}

/**
 * Provides test configurations for Redshift connection tests.
 * 
 * Reads configuration from secrets/config.json and creates variations
 * for testing connection failures.
 */
object RedshiftTestConfigProvider {
    
    private val CONFIG_PATH = "secrets/config.json"
    private val mapper = ObjectMapper()
    
    private val baseConfig: JsonNode? by lazy {
        loadConfig()
    }
    
    private fun loadConfig(): JsonNode? {
        return try {
            val configPath = Paths.get(CONFIG_PATH)
            if (Files.exists(configPath)) {
                val configContent = Files.readString(configPath)
                mapper.readTree(configContent)
            } else {
                log.warn { "Config file not found at $CONFIG_PATH - tests will be skipped" }
                null
            }
        } catch (e: Exception) {
            log.warn(e) { "Failed to load config from $CONFIG_PATH - tests will be skipped" }
            null
        }
    }
    
    fun hasValidConfig(): Boolean = baseConfig != null
    
    fun getValidConfig(): String {
        return baseConfig?.toString() 
            ?: throw IllegalStateException("No valid config available")
    }
    
    fun getConfigWithIncorrectPassword(): String {
        val config = baseConfig?.deepCopy() as? ObjectNode
            ?: throw IllegalStateException("No valid config available")
        config.put("password", "fake_password_12345")
        return config.toString()
    }
    
    fun getConfigWithIncorrectUsername(): String {
        val config = baseConfig?.deepCopy() as? ObjectNode
            ?: throw IllegalStateException("No valid config available")
        config.put("username", "fake_user_12345")
        return config.toString()
    }
    
    fun getConfigWithIncorrectHost(): String {
        val config = baseConfig?.deepCopy() as? ObjectNode
            ?: throw IllegalStateException("No valid config available")
        config.put("host", "localhost2.invalid.example.com")
        return config.toString()
    }
    
    fun getConfigWithIncorrectDatabase(): String {
        val config = baseConfig?.deepCopy() as? ObjectNode
            ?: throw IllegalStateException("No valid config available")
        config.put("database", "wrongdatabase_12345")
        return config.toString()
    }
}
