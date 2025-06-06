/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

interface HttpClient {
    fun sendRequest(request: Request): Response
}
