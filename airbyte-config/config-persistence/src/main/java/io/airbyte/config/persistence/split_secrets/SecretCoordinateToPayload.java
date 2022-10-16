/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

public record SecretCoordinateToPayload(SecretCoordinate secretCoordinate,
                                        String payload,
                                        JsonNode secretCoordinateForDB) {

}
