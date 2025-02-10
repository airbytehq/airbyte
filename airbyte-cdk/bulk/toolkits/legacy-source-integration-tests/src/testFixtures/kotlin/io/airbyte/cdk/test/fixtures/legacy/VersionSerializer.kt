/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.SerializerProvider
import com.fasterxml.jackson.databind.ser.std.StdSerializer
import java.io.IOException

class VersionSerializer @JvmOverloads constructor(t: Class<Version>? = null) :
    StdSerializer<Version>(t) {
    @Throws(IOException::class)
    override fun serialize(value: Version, gen: JsonGenerator, provider: SerializerProvider) {
        gen.writeStartObject()
        gen.writeStringField("version", value.version)
        gen.writeEndObject()
    }
}
