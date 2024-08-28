/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.functional

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*

private val LOGGER = KotlinLogging.logger {}
/**
 * A class that represents a value of one of two possible types (a disjoint union). An instance of
 * Either is an instance of Left or Right.
 *
 * A common use of Either is for error handling in functional programming. By convention, Left is
 * failure and Right is success.
 *
 * @param <Error> the type of the left value
 * @param <Result> the type of the right value </Result></Error>
 */
class Either<Error, Result> private constructor(left: Error?, right: Result?) {
    val left: Error? = left
    val right: Result? = right

    fun isLeft(): Boolean {
        return left != null
    }

    fun isRight(): Boolean {
        return right != null
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val either = other as Either<*, *>
        return left == either.left && right == either.right
    }

    override fun hashCode(): Int {
        return Objects.hash(left, right)
    }

    companion object {
        fun <Error, Result> left(error: Error): Either<Error, Result> {
            if (error == null) {
                LOGGER.warn { "Either.left called with a null!" }
            }
            return Either(error!!, null)
        }

        fun <Error, Result> right(result: Result): Either<Error, Result> {
            if (result == null) {
                // I ran into this when declaring a functional class of <Void>.
                // In java, we must return null because Void has no instanciation
                // In kotlin, though, we should change the return type to <Unit> and return Unit
                LOGGER.warn { "Either.right called with a null!" }
            }
            return Either(null, result)
        }
    }
}
