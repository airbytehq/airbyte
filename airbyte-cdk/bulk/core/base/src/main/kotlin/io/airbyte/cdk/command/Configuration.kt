/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

/**
 * Interface that defines a typed connector configuration.
 *
 * Prefer this or its implementations over the corresponding configuration POJOs; i.e.
 * [ConfigurationSpecification] subclasses.
 */
interface Configuration
