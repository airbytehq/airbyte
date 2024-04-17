import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.kotlinModule
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class DatabricksConnectorConfigTest {

    // Write a test for DatabricksConnectorConfig deserialization
    @Test
    fun testDeserialization() {
        val jsonString = MoreResources.readResource("basic-config.json");
        val objectMapper = MoreMappers.initMapper()
        objectMapper.registerModule(kotlinModule())
        val deserializedConfig:DatabricksConnectorConfig = objectMapper.readValue<DatabricksConnectorConfig>(jsonString, DatabricksConnectorConfig::class.java)
//        assertEquals(config, deserializedConfig)
        println(jsonString)
        println(deserializedConfig)
    }
}
