package io.airbyte.integrations.destination.snowflake.caching

import java.util.concurrent.ConcurrentHashMap
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler
import org.slf4j.Logger
import org.slf4j.LoggerFactory

object CacheManager {
    private val cache = ConcurrentHashMap<String, CacheEntry>()
    private const val CACHE_DURATION_MILLIS = 60 * 60 * 1000 // 1 hour

    fun queryJsons(database: JdbcDatabase,
                   query: String,
                   parameters: Array<String>): List<JsonNode> {

        LOGGER.info("Entering CacheManager.queryJsons with: cache.size()=" + cache.size
            + "\nquery=" + query
            + "\n\nparameters=" + parameters)

        if(cache.size > 0) {
            LOGGER.info("Inside CacheManager: Cache contains existing entries: cache.size()=" + cache.size)
        } else {
            LOGGER.info("Inside CacheManager: Cache is empty: cache.size()=" + cache.size)
        }
        
        // Replace the placeholders with the actual values
        var updatedQuery = query
        parameters.forEach { value ->
            updatedQuery = updatedQuery.replaceFirst("?", value)
        }

        // Print the resulting string
        LOGGER.info("updatedQuery=" + updatedQuery)

        if( ! updatedQuery.contains("information_schema")) {
            //return database.queryJsons(updatedQuery)
            return database.queryJsons(query, *parameters)
        }

        val cachedResult = CacheManager.getFromCache(updatedQuery)
        if (cachedResult != null) {

            LOGGER.info("Found result in cache for updatedQuery=" + updatedQuery)

            return cachedResult
        }

        // Cache miss, execute query
        lateinit var resultSet: List<JsonNode>

        try {

            //resultSet = database.queryJsons(updatedQuery)

            resultSet = database.queryJsons(query, *parameters)

            // Cache the result
            putInCache(query, resultSet)

        } catch (e: Exception) {
            e.printStackTrace()
        }

        return resultSet
    }

    fun getFromCache(query: String): List<JsonNode>? {
        val currentTime = System.currentTimeMillis()
        val cacheEntry = cache[query]

        if (cacheEntry != null && (currentTime - cacheEntry.timestamp < CACHE_DURATION_MILLIS)) {
            // Return cached result if it's still valid
            return cacheEntry.resultSet
        }

        // Cache expired or entry does not exist
        return null
    }

    fun putInCache(query: String, resultSet: List<JsonNode>) {
        cache[query] = CacheEntry(resultSet, System.currentTimeMillis())
    }

    private data class CacheEntry(val resultSet: List<JsonNode>, val timestamp: Long)

    private val LOGGER: Logger =
            LoggerFactory.getLogger(SnowflakeDestinationHandler::class.java)

}
