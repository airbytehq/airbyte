package io.airbyte.cdk.load.interpolation

import kotlin.test.assertFalse
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

class BooleanInterpolatorTest {

    @Test
    internal fun `test given true statement when eval then return true`() {
        val string = "{{ 2 == 1 + 1 }}"
        assertTrue { BooleanInterpolator().interpolate(string, emptyMap()) }
    }

    @Test
    internal fun `test given false statement when eval then return false`() {
        val string = "{{ 11 == 1 + 1 }}"
        assertFalse { BooleanInterpolator().interpolate(string, emptyMap()) }
    }

    @Test
    internal fun `test given string that represent true bool when eval then return true`() {
        val string = "TrUE"
        assertTrue { BooleanInterpolator().interpolate(string, emptyMap()) }
    }

    @Test
    internal fun `test given any string that is not true case insensitive that represent true bool when eval then return false`() {
        val string = "toto"
        assertFalse { BooleanInterpolator().interpolate(string, emptyMap()) }
    }

}
