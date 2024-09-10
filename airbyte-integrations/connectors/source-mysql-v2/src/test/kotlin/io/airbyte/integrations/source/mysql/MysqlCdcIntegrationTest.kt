package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.ConfiguredCatalogFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MysqlCdcIntegrationTest {
    @Inject
    lateinit var supplier: ConfigurationJsonObjectSupplier<MysqlSourceConfigurationJsonObject>

    @Inject
    lateinit var catalogFactory: ConfiguredCatalogFactory

    @Test
    @Property(name = "airbyte.connector.config.json", value = CDC_CONFIG_JSON)
    @Property(name = "airbyte.connector.catalog.json", value = CDC_CATALOG)
    fun testRead() {
        val pojoConfig: MysqlSourceConfigurationJsonObject = supplier.get()
        val configuredCatalog = catalogFactory.make(CDC_CATALOG)
        val output: BufferingOutputConsumer = CliRunner.runSource("read", pojoConfig, configuredCatalog)
        Assertions.assertNotNull(output.specs())
    }
}

const val CDC_CONFIG_JSON =
    """
{
  "host": "34.106.250.115",
  "port": 3306,
  "username": "root",
  "password": "***",
  "schemas": [
    "1gb"
  ],
  "encryption": {
    "encryption_method": "preferred"
  },
  "tunnel_method": {
    "tunnel_method": "NO_TUNNEL"
  },
  "cursor": {
    "cursor_method": "cdc"
  },
  "checkpoint_target_interval_seconds": 300,
  "concurrency": 1
}
"""

const val CDC_CATALOG =
    """
{
   "streams":[
      {
         "stream":{
            "name":"newcdk_table",
            "namespace":"1gb",
            "json_schema":{
               "type":"object",
               "properties":{
                  "id":{
                     "type":"number",
                     "airbyte_type":"integer"
                  },
                  "value":{
                     "type":"string"
                  }
               }
            },
            "is_resumable":true,
            "default_cursor_field":[
               
            ],
            "supported_sync_modes":[
               "full_refresh",
               "incremental"
            ],
            "source_defined_cursor":false,
            "source_defined_primary_key":[
               [
                  "id"
               ]
            ]
         },
         "mappers":[
            
         ],
         "sync_mode":"incremental",
         "primary_key":[
            [
               "id"
            ]
         ],
         "cursor_field":[
            "id"
         ],
         "destination_sync_mode":"append_dedup"
      }
   ]
}
"""
