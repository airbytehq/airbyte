/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.envclient.dto;

public record EnvironmentRequest(

                                 String name,

                                 OperationRequest request

) {}
