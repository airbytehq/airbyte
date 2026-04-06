/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

interface HttpClient {
    fun send(request: Request): Response
}
