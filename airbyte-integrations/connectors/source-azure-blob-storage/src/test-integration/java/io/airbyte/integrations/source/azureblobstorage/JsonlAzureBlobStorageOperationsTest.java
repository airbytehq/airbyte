/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import static org.assertj.core.api.Assertions.assertThat;

import com.azure.core.util.BinaryData;
import com.azure.storage.blob.BlobContainerClient;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.source.azureblobstorage.format.JsonlAzureBlobStorageOperations;
import java.time.OffsetDateTime;
import org.json.JSONException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.skyscreamer.jsonassert.JSONAssert;

class JsonlAzureBlobStorageOperationsTest {

  private AzureBlobStorageContainer azureBlobStorageContainer;

  private AzureBlobStorageOperations azureBlobStorageOperations;

  private BlobContainerClient blobContainerClient;

  private ObjectMapper objectMapper;

  private static final String STREAM_NAME = "airbyte-container";

  @BeforeEach
  void setup() {
    azureBlobStorageContainer = new AzureBlobStorageContainer().withExposedPorts(10000);
    azureBlobStorageContainer.start();
    JsonNode jsonConfig = AzureBlobStorageDataFactory.createAzureBlobStorageConfig(
        "http://127.0.0.1:" + azureBlobStorageContainer.getMappedPort(10000), STREAM_NAME);

    var azureBlobStorageConfig = AzureBlobStorageConfig.createAzureBlobStorageConfig(jsonConfig);
    blobContainerClient = azureBlobStorageConfig.createBlobContainerClient();
    blobContainerClient.createIfNotExists();
    blobContainerClient.getBlobClient("FolderA/FolderB/blob1.json").upload(BinaryData
        .fromString("""
                    {"name":"Molecule Man","age":29,"secretIdentity":"Dan Jukes","powers":["Radiation resistance","Turning tiny","Radiation blast"]}
                    {"name":"Bat Man","secretIdentity":"Bruce Wayne","powers":["Agility", "Detective skills", "Determination"]}
                    """));
    blobContainerClient.getBlobClient("FolderA/FolderB/blob2.json").upload(BinaryData.fromString(
        "{\"name\":\"Molecule Man\",\"surname\":\"Powers\",\"powers\":[\"Radiation resistance\",\"Turning tiny\",\"Radiation blast\"]}\n"));
    // should be ignored since its in ignored path
    blobContainerClient.getBlobClient("FolderA/blob3.json").upload(BinaryData.fromString("{\"ignored\":true}\n"));
    azureBlobStorageOperations = new JsonlAzureBlobStorageOperations(azureBlobStorageConfig);
    objectMapper = new ObjectMapper();
  }

  @AfterEach
  void tearDown() {
    azureBlobStorageContainer.stop();
    azureBlobStorageContainer.close();
  }

  @Test
  void testListBlobs() {
    var azureBlobs = azureBlobStorageOperations.listBlobs();

    assertThat(azureBlobs)
        .hasSize(2)
        .anyMatch(ab -> ab.name().equals("FolderA/FolderB/blob1.json"))
        .anyMatch(ab -> ab.name().equals("FolderA/FolderB/blob2.json"));
  }

  @Test
  void testInferSchema() throws JsonProcessingException, JSONException {

    var jsonSchema = azureBlobStorageOperations.inferSchema();

    JSONAssert.assertEquals(objectMapper.writeValueAsString(jsonSchema), """
                                                                         {
                                                                         	"$schema": "http://json-schema.org/draft-07/schema#",
                                                                         	"type": "object",
                                                                         	"properties": {
                                                                         		"name": {
                                                                         			"type": "string"
                                                                         		},
                                                                         		"age": {
                                                                         			"type": "integer"
                                                                         		},
                                                                         		"secretIdentity": {
                                                                         			"type": "string"
                                                                         		},
                                                                         		"powers": {
                                                                         			"type": "array",
                                                                         			"items": {
                                                                         				"type": "string"
                                                                         			}
                                                                         		},
                                                                         		"surname": {
                                                                         			"type": "string"
                                                                         		},
                                                                         		"_ab_source_blob_name": {
                                                                         			"type": "string"
                                                                         		},
                                                                         		"_ab_source_file_last_modified": {
                                                                         			"type": "string"
                                                                         		}
                                                                         	},
                                                                         	"additionalProperties": true
                                                                         }
                                                                         """, true);

  }

  @Test
  void testReadBlobs() throws InterruptedException, JsonProcessingException, JSONException {
    var now = OffsetDateTime.now();

    Thread.sleep(1000);

    blobContainerClient.getBlobClient("FolderA/FolderB/blob1.json").upload(BinaryData.fromString(
        "{\"name\":\"Super Man\",\"secretIdentity\":\"Clark Kent\",\"powers\":[\"Lightning fast\",\"Super strength\",\"Laser vision\"]}\n"),
        true);

    var messages = azureBlobStorageOperations.readBlobs(now);

    var azureBlob = azureBlobStorageOperations.listBlobs().stream()
        .filter(ab -> ab.name().equals("FolderA/FolderB/blob1.json"))
        .findAny()
        .orElseThrow();

    assertThat(messages)
        .hasSize(1);

    JSONAssert.assertEquals(objectMapper.writeValueAsString(messages.get(0)), String.format(
        "{\"name\":\"Super Man\",\"secretIdentity\":\"Clark Kent\",\"powers\":[\"Lightning fast\",\"Super strength\",\"Laser vision\"],\"_ab_source_blob_name\":\"%s\",\"_ab_source_file_last_modified\":\"%s\"}\n",
        azureBlob.name(), azureBlob.lastModified().toString()), true);

  }

}
