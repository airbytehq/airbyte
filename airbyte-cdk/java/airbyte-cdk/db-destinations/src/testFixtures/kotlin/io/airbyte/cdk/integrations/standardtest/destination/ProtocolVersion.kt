/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

enum class ProtocolVersion(val prefix: String) {
    V0("v0"),
    V1("v1")
}
