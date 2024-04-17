import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.module.kotlin.kotlinModule
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.resources.MoreResources
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import org.junit.jupiter.api.Test

class DatabricksConnectorConfigTest {

    // Write a test for DatabricksConnectorConfig deserialization
    @Test
    fun testDeserialization() {
        val jsonString = MoreResources.readResource("basic-config.json");
        val objectMapper = MoreMappers.initMapper()
        objectMapper.registerModule(kotlinModule())
        val jsonNode = objectMapper.readValue(jsonString, JsonNode::class.java)
        val typedConfig = DatabricksConnectorConfig.deserialize(jsonNode)
        println(jsonString)
        println(typedConfig)
    }
}
