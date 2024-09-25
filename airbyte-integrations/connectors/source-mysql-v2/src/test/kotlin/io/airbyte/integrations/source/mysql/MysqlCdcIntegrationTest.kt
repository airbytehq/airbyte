/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.ConfiguredCatalogFactory
import io.airbyte.cdk.command.InputStateFactory
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.AirbyteStateMessage
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
@Disabled
class MysqlCdcIntegrationTest {
    @Inject
    lateinit var supplier: ConfigurationJsonObjectSupplier<MysqlSourceConfigurationJsonObject>

    @Inject lateinit var catalogFactory: ConfiguredCatalogFactory

    @Inject lateinit var inputStateFactory: InputStateFactory

    @Test
    @Property(name = "airbyte.connector.config.json", value = CDC_CONFIG_JSON)
    @Property(name = "airbyte.connector.catalog.json", value = CDC_CATALOG)
    fun testReadWithState() {
        val pojoConfig: MysqlSourceConfigurationJsonObject = supplier.get()
        val configuredCatalog = catalogFactory.make(CDC_CATALOG)
        val list: List<io.airbyte.protocol.models.v0.AirbyteStateMessage>? =
            ValidatedJsonUtils.parseList(
                    io.airbyte.protocol.models.v0.AirbyteStateMessage::class.java,
                    AIRBYTE_STATE_MESSAGE_JSON_2
                )
                // Discard states messages with unset type to allow {} as a valid input state.
                .filter { it.type != null }

        print(list)
        // val inputState = inputStateFactory.make(AIRBYTE_STATE_MESSAGE)
        // println(inputState)
        // val output: BufferingOutputConsumer = CliRunner.runSource("read", pojoConfig,
        // configuredCatalog)
        val output: BufferingOutputConsumer =
            CliRunner.source("read", pojoConfig, configuredCatalog, list).run()
        Assertions.assertNotNull(output.specs())
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CDC_CONFIG_JSON)
    @Property(name = "airbyte.connector.catalog.json", value = CDC_CATALOG)
    fun testReadNoState() {
        val pojoConfig: MysqlSourceConfigurationJsonObject = supplier.get()
        val configuredCatalog = catalogFactory.make(CDC_CATALOG)
        val output: BufferingOutputConsumer =
            CliRunner.source("read", pojoConfig, configuredCatalog).run()
        Assertions.assertNotNull(output.specs())
    }
}

const val CDC_CONFIG_JSON =
    """
{
  "host": "34.106.250.115",
  "port": 3306,
  "username": "root",
  "password": "*******",
  "schemas": [
    "newcdk"
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
  "concurrency": 2
}
"""

const val CDC_CATALOG =
    """
{
   "streams":[
      {
         "stream":{
            "name":"newcdk_table",
            "namespace":"newcdk",
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

// This is the json that the AirbyteStateMessage produces for global messages
const val AIRBYTE_STATE_MESSAGE_JSON =
    """
{
  "type": "GLOBAL",
  "global": {
    "shared_state": {
        "state": {
            "is_compressed": false,
            "mysql_cdc_offset": {
                "[\"newcdk\",{\"server\":\"newcdk\"}]": "{\"file\":\"mysql-bin.000537\",\"pos\":197,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367418\",\"server_id\":4227249085}"
            },
            "mysql_db_history": 
            "{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290992,\"databaseName\":\"\",\"ddl\":\"SET character_set_server=utf8mb4, collation_server=utf8mb4_0900_ai_ci\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290993,\"databaseName\":\"newcdk\",\"ddl\":\"DROP TABLE IF EXISTS `newcdk`.`newcdk_table`\",\"tableChanges\":[{\"type\":\"DROP\",\"id\":\"\\\"newcdk\\\".\\\"newcdk_table\\\"\"}]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290997,\"databaseName\":\"newcdk\",\"ddl\":\"DROP DATABASE IF EXISTS `newcdk`\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290998,\"databaseName\":\"newcdk\",\"ddl\":\"CREATE DATABASE `newcdk` CHARSET utf8mb4 COLLATE utf8mb4_0900_ai_ci\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290998,\"databaseName\":\"newcdk\",\"ddl\":\"USE `newcdk`\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172291,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172291004,\"databaseName\":\"newcdk\",\"ddl\":\"CREATE TABLE `newcdk_table` (\\n  `id` int NOT NULL AUTO_INCREMENT,\\n  `value` varchar(255) NOT NULL,\\n  PRIMARY KEY (`id`)\\n) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci\",\"tableChanges\":[{\"type\":\"CREATE\",\"id\":\"\\\"newcdk\\\".\\\"newcdk_table\\\"\",\"table\":{\"defaultCharsetName\":\"utf8mb4\",\"primaryKeyColumnNames\":[\"id\"],\"columns\":[{\"name\":\"id\",\"jdbcType\":4,\"typeName\":\"INT\",\"typeExpression\":\"INT\",\"charsetName\":null,\"position\":1,\"optional\":false,\"autoIncremented\":true,\"generated\":true,\"comment\":null,\"hasDefaultValue\":false,\"enumValues\":[]},{\"name\":\"value\",\"jdbcType\":12,\"typeName\":\"VARCHAR\",\"typeExpression\":\"VARCHAR\",\"charsetName\":\"utf8mb4\",\"length\":255,\"position\":2,\"optional\":false,\"autoIncremented\":false,\"generated\":false,\"comment\":null,\"hasDefaultValue\":false,\"enumValues\":[]}],\"attributes\":[]},\"comment\":null}]}\n"
        }
    },
    "stream_states": [
      {
        "stream_descriptor": {
          "name": "newcdk_table",
          "namespace": "newcdk",
          "additionalProperties": {}
        },
        "stream_state": {
          "stream_name": "newcdk_table",
          "stream_namespace": "newcdk",
          "cursor_field": []
        },
        "additionalProperties": {}
      }
    ]
  },
  "sourceStats": {
    "recordCount": 1.0,
    "additionalProperties": {}
  },
  "additionalProperties": {}
}
    """

// This is the json that the AirbyteStateMessage produces for global messages
// Offset until msg 13
const val AIRBYTE_STATE_MESSAGE_JSON_2 =
    """
{
  "type": "GLOBAL",
  "global": {
    "shared_state": {
        "state": {
            "is_compressed": false,
            "mysql_cdc_offset":{
                 "[\"newcdk\",{\"server\":\"newcdk\"}]": "{\"ts_sec\":1726523809,\"file\":\"mysql-bin.000538\",\"pos\":2127,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367425\",\"row\":1,\"server_id\":4227249085,\"event\":2}"
            },
            "mysql_db_history":
            "{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290992,\"databaseName\":\"\",\"ddl\":\"SET character_set_server=utf8mb4, collation_server=utf8mb4_0900_ai_ci\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290993,\"databaseName\":\"newcdk\",\"ddl\":\"DROP TABLE IF EXISTS `newcdk`.`newcdk_table`\",\"tableChanges\":[{\"type\":\"DROP\",\"id\":\"\\\"newcdk\\\".\\\"newcdk_table\\\"\"}]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290997,\"databaseName\":\"newcdk\",\"ddl\":\"DROP DATABASE IF EXISTS `newcdk`\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290998,\"databaseName\":\"newcdk\",\"ddl\":\"CREATE DATABASE `newcdk` CHARSET utf8mb4 COLLATE utf8mb4_0900_ai_ci\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290998,\"databaseName\":\"newcdk\",\"ddl\":\"USE `newcdk`\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172291,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172291004,\"databaseName\":\"newcdk\",\"ddl\":\"CREATE TABLE `newcdk_table` (\\n  `id` int NOT NULL AUTO_INCREMENT,\\n  `value` varchar(255) NOT NULL,\\n  PRIMARY KEY (`id`)\\n) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci\",\"tableChanges\":[{\"type\":\"CREATE\",\"id\":\"\\\"newcdk\\\".\\\"newcdk_table\\\"\",\"table\":{\"defaultCharsetName\":\"utf8mb4\",\"primaryKeyColumnNames\":[\"id\"],\"columns\":[{\"name\":\"id\",\"jdbcType\":4,\"typeName\":\"INT\",\"typeExpression\":\"INT\",\"charsetName\":null,\"position\":1,\"optional\":false,\"autoIncremented\":true,\"generated\":true,\"comment\":null,\"hasDefaultValue\":false,\"enumValues\":[]},{\"name\":\"value\",\"jdbcType\":12,\"typeName\":\"VARCHAR\",\"typeExpression\":\"VARCHAR\",\"charsetName\":\"utf8mb4\",\"length\":255,\"position\":2,\"optional\":false,\"autoIncremented\":false,\"generated\":false,\"comment\":null,\"hasDefaultValue\":false,\"enumValues\":[]}],\"attributes\":[]},\"comment\":null}]}\n"
        }
    },
    "stream_states": [
      {
        "stream_descriptor": {
          "name": "newcdk_table",
          "namespace": "newcdk",
          "additionalProperties": {}
        },
        "stream_state": {
          "stream_name": "newcdk_table",
          "stream_namespace": "newcdk",
          "cursor_field": []
        },
        "additionalProperties": {}
      }
    ]
  },
  "sourceStats": {
    "recordCount": 1.0,
    "additionalProperties": {}
  },
  "additionalProperties": {}
}
    """

// State that is copied from the platform

const val STATE = // As of 9/15/2024
    """
{
  "shared_state": {
    "state": {
      "is_compressed": false,
      "mysql_cdc_offset": {
        "[\"newcdk\",{\"server\":\"newcdk\"}]": "{\"file\":\"mysql-bin.000537\",\"pos\":197,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367418\",\"server_id\":4227249085}"
      },
      "mysql_db_history": "{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290992,\"databaseName\":\"\",\"ddl\":\"SET character_set_server=utf8mb4, collation_server=utf8mb4_0900_ai_ci\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290993,\"databaseName\":\"newcdk\",\"ddl\":\"DROP TABLE IF EXISTS `newcdk`.`newcdk_table`\",\"tableChanges\":[{\"type\":\"DROP\",\"id\":\"\\\"newcdk\\\".\\\"newcdk_table\\\"\"}]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290997,\"databaseName\":\"newcdk\",\"ddl\":\"DROP DATABASE IF EXISTS `newcdk`\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290998,\"databaseName\":\"newcdk\",\"ddl\":\"CREATE DATABASE `newcdk` CHARSET utf8mb4 COLLATE utf8mb4_0900_ai_ci\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172290,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172290998,\"databaseName\":\"newcdk\",\"ddl\":\"USE `newcdk`\",\"tableChanges\":[]}\n{\"source\":{\"server\":\"newcdk\"},\"position\":{\"ts_sec\":1726172291,\"file\":\"mysql-bin.000534\",\"pos\":1183,\"gtids\":\"f56101bf-227f-11ee-af5d-42010ab40020:1-3367414\",\"snapshot\":true},\"ts_ms\":1726172291004,\"databaseName\":\"newcdk\",\"ddl\":\"CREATE TABLE `newcdk_table` (\\n  `id` int NOT NULL AUTO_INCREMENT,\\n  `value` varchar(255) NOT NULL,\\n  PRIMARY KEY (`id`)\\n) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci\",\"tableChanges\":[{\"type\":\"CREATE\",\"id\":\"\\\"newcdk\\\".\\\"newcdk_table\\\"\",\"table\":{\"defaultCharsetName\":\"utf8mb4\",\"primaryKeyColumnNames\":[\"id\"],\"columns\":[{\"name\":\"id\",\"jdbcType\":4,\"typeName\":\"INT\",\"typeExpression\":\"INT\",\"charsetName\":null,\"position\":1,\"optional\":false,\"autoIncremented\":true,\"generated\":true,\"comment\":null,\"hasDefaultValue\":false,\"enumValues\":[]},{\"name\":\"value\",\"jdbcType\":12,\"typeName\":\"VARCHAR\",\"typeExpression\":\"VARCHAR\",\"charsetName\":\"utf8mb4\",\"length\":255,\"position\":2,\"optional\":false,\"autoIncremented\":false,\"generated\":false,\"comment\":null,\"hasDefaultValue\":false,\"enumValues\":[]}],\"attributes\":[]},\"comment\":null}]}\n"
    }
  },
  "streamStates": [
    {
      "streamDescriptor": {
        "name": "newcdk_table",
        "namespace": "newcdk"
      },
      "streamState": {
        "stream_name": "newcdk_table",
        "cursor_field": [
          "_ab_cdc_cursor"
        ],
        "stream_namespace": "newcdk"
      }
    }
  ]
}
    """
