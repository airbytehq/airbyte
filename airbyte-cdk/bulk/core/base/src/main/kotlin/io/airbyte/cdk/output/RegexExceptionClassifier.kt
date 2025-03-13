/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.micronaut.context.annotation.EachProperty
import io.micronaut.context.annotation.Parameter
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

const val REGEX_CLASSIFIER_PREFIX = "${EXCEPTION_CLASSIFIER_PREFIX}.regex"

/** [ExceptionClassifier] implementation based on regexes applied to the exception message. */
@Singleton
@Requires(property = "${REGEX_CLASSIFIER_PREFIX}.rules")
class RegexExceptionClassifier(
    @Value("\${${REGEX_CLASSIFIER_PREFIX}.order:10}") override val orderValue: Int,
    override val rules: List<RegexExceptionClassifierRule>,
) : RuleBasedExceptionClassifier<RegexExceptionClassifierRule> {

    init {
        for (rule in rules) {
            rule.validate()
        }
    }
}

/** Micronaut configuration object for [RuleBasedExceptionClassifier] rules. */
@EachProperty("${REGEX_CLASSIFIER_PREFIX}.rules", list = true)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class RegexExceptionClassifierRule(
    @param:Parameter override val ordinal: Int,
) : RuleBasedExceptionClassifier.Rule {

    // Micronaut configuration objects work better with mutable properties.
    override lateinit var error: RuleBasedExceptionClassifier.ErrorKind
    lateinit var pattern: String
    lateinit var inputExample: String
    override var group: String? = null
    override var output: String? = null
    override var referenceLinks: List<String> = emptyList()

    val regex: Regex by lazy {
        pattern.toRegex(setOf(RegexOption.MULTILINE, RegexOption.IGNORE_CASE))
    }

    override fun matches(e: Throwable): Boolean =
        e.message?.let { regex.containsMatchIn(it) } ?: false

    override fun validate() {
        require(runCatching { error }.isSuccess) { "error kind must be set" }
        require(runCatching { pattern }.isSuccess) { "regex pattern must be set" }
        require(runCatching { inputExample }.isSuccess) {
            "input exception message example must be set"
        }
        val compileResult: Result<Regex> = runCatching { regex }
        require(compileResult.isSuccess) {
            "regex pattern error: ${compileResult.exceptionOrNull()?.message}"
        }
    }
}
