/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.manifest;

public class Entry {

  public final String url;
  public final Boolean mandatory;

  public Entry(String url, Boolean mandatory) {
    this.url = url;
    this.mandatory = mandatory;
  }

  public Entry(String url) {
    this(url, true);
  }

}
