/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.manifest;

public class Entry {

  public final String url;
  public final Boolean mandatory;

  public Entry(final String url, final Boolean mandatory) {
    this.url = url;
    this.mandatory = mandatory;
  }

  public Entry(final String url) {
    this(url, true);
  }

}
