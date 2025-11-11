/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import java.math.BigDecimal
import java.math.BigInteger

open class BigDecimalUtil {
    /** Returns the largest representable BigDecimal for a given (precision, scale) pair. */
    open fun maxForRange(precision: Int, scale: Int) =
        BigDecimal(BigInteger("9".repeat(precision)), scale)
}

/**
 * Calculate the precision (i.e. number of digits) in this BigDecimal, according to how Bigquery
 * represents it.
 *
 * For BigDecimal instances with nonzero decimal points and 0 trailing 0-digits (e.g. `123.456`,
 * `123`), this is equivalent to [BigDecimal.precision()].
 *
 * For BigDecimal instances with zero decimal points and some trailing 0-digits (e.g. `10`, `100`),
 * this function calculates the total number of digits in the number.
 */
fun BigDecimal.normalizedPrecision(): Int =
    if (this.scale() >= 0) {
        this.precision()
    } else {
        this.precision() - this.scale()
    }

/**
 * Calculate the scale (i.e. number of decimal points) in this BigDecimal, according to how Bigquery
 * represents it.
 *
 * For BigDecimal instances with nonzero decimal points and 0 trailing 0-digits (e.g. `123.456`,
 * `123`), this is equivalent to [BigDecimal.scale()].
 *
 * For BigDecimal instances with zero decimal points and some trailing 0-digits (e.g. `10`, `100`),
 * this function returns zero.
 */
fun BigDecimal.normalizedScale(): Int =
    if (this.scale() >= 0) {
        this.scale()
    } else {
        0
    }
