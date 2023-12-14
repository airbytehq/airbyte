/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata.envclient.dto;

public record CreateEnvironmentRequest(

                                       String name,

                                       String region,

                                       String password

) {

}
