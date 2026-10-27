/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.check

import io.airbyte.cdk.command.ConfigurationSpecification

/**
 * Name of the optional top-level key of the configuration JSON object which turns a CHECK into a
 * section check. Its value names one of the sections the connector declares in its specification
 * (`sections[].id`); the configuration is then only expected to hold the fields of that section and
 * of the sections before it, and CHECK validates that much only. Without the key, CHECK validates
 * the complete configuration.
 */
const val CHECK_SECTION_KEY = "check-section"

/**
 * Connector-provided bean which makes CHECK section-aware, for the stepped setup form.
 *
 * A connector whose specification declares `sections` (each listing the `groups` of properties it
 * shows) can be checked one section at a time: the configuration JSON then carries a top-level
 * [CHECK_SECTION_KEY] key naming the section, and only holds the fields of that section and of the
 * sections before it. [CheckOperation] resolves the section against the specification and calls
 * [check] for every section but the last one; the last section completes the configuration, so it
 * gets the full check, exactly as a CHECK without [CHECK_SECTION_KEY] does.
 *
 * [check] validates the configuration up to [section] and no further: the fields of that section,
 * the fields of earlier sections it depends on (checking credentials needs the host, the port and
 * the tunnel), and the server-side prerequisites those fields describe. It must not expect any
 * other field to be present. A missing or invalid field is reported by throwing a
 * [io.airbyte.cdk.ConfigErrorException] whose message names the field. The dependencies between
 * sections are the connector's to define, with the specification ordering sections so that no
 * section relies on a later one.
 */
interface CheckSectionHandler<T : ConfigurationSpecification> {
    fun check(section: String, pojo: T)
}
