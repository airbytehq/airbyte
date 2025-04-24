/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule

/**
 * The [JavaTimeModule] allows mappers to accommodate different varieties of serialised date time
 * strings.
 *
 * All jackson mapper creation should use the following methods for instantiation.
 */
object MoreMappers {
    @JvmStatic
    fun initMapper(): ObjectMapper {
        val result = ObjectMapper().registerModule(JavaTimeModule())
        result.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
        result.configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
        return result
    }

    @JvmStatic
    fun initYamlMapper(factory: YAMLFactory?): ObjectMapper {
        return ObjectMapper(factory).registerModule(JavaTimeModule())
    }
}
