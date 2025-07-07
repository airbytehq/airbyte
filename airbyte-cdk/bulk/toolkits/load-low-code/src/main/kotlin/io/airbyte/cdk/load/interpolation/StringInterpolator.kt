/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.interpolation

import com.hubspot.jinjava.Jinjava

class StringInterpolator {
    private val interpolator = Jinjava()

    fun interpolate(string: String, context: Map<String, Any>): String {
        return interpolator.render(string, context)
    }
}
