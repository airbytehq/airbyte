/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

/**
 * In general, callers should not directly instantiate this class. Use
 * {@link SqlGenerator#buildColumnId(String)} instead.
 *
 * @param name the name of the column in the final table. Callers should prefer
 *        {@link #name(String)} when using the column in a query.
 * @param originalName the name of the field in the raw JSON blob
 * @param canonicalName the name of the field according to the destination. Used for deduping.
 *        Useful if a destination warehouse handles columns ignoring case, but preserves case in the
 *        table schema.
 */
public record ColumnId(String name, String originalName, String canonicalName) {

  public String name(final String quote) {
    return quote + name + quote;
  }

}
