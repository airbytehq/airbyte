package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

public record SecretCoordinateToPayload(SecretCoordinate secretCoordinate, String payload,
                                        JsonNode secretCoordinateForDB) {

  public JsonNode getSecretCoordinateForDB() {
    return secretCoordinateForDB;
  }

  public SecretCoordinateToPayload(SecretCoordinate secretCoordinate, String payload, JsonNode secretCoordinateForDB) {
    this.secretCoordinate = secretCoordinate;
    this.payload = payload;
    this.secretCoordinateForDB = secretCoordinateForDB.deepCopy();
  }

  public SecretCoordinate getSecretCoordinate() {
    return secretCoordinate;
  }

  public String getPayload() {
    return payload;
  }

}
