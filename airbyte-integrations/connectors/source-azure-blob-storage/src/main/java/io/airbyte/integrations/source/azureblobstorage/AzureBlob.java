/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import java.time.OffsetDateTime;

public record AzureBlob(

                        String name,

                        OffsetDateTime lastModified

) {

  public static class Builder {

    private String name;

    private OffsetDateTime lastModified;

    public Builder withName(String name) {
      this.name = name;
      return this;
    }

    public Builder withLastModified(OffsetDateTime lastModified) {
      this.lastModified = lastModified;
      return this;
    }

    public AzureBlob build() {
      return new AzureBlob(name, lastModified);
    }

  }

}
