/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.interpolation

import io.pebbletemplates.pebble.PebbleEngine
import io.pebbletemplates.pebble.loader.StringLoader
import io.pebbletemplates.pebble.template.PebbleTemplate
import java.io.StringWriter
import java.io.Writer

class StringInterpolator {
    private val engine: PebbleEngine = PebbleEngine.Builder().loader(StringLoader()).build()

    fun interpolate(string: String, context: Map<String, Any>): String {
        val template: PebbleTemplate = engine.getTemplate(string)

        val writer: Writer = StringWriter()
        template.evaluate(writer, context)
        return writer.toString()
    }
}
