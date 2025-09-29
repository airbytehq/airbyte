package io.airbyte.cdk.load.interpolation

class BooleanInterpolator(
    private val stringInterpolator: StringInterpolator = StringInterpolator()
) {

    fun interpolate(string: String, context: Map<String, Any>): Boolean {
        return stringInterpolator.interpolate(string, context).toBoolean()
    }
}
