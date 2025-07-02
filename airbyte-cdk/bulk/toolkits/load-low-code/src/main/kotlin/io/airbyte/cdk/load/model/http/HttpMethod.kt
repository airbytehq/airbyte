package io.airbyte.cdk.load.model.http

/**
 * Enum representing HTTP methods supported by the HttpRequester.
 */
enum class HttpMethod {
    GET,
    POST,
    PUT,
    PATCH,
    DELETE,
    HEAD,
    OPTIONS
} 