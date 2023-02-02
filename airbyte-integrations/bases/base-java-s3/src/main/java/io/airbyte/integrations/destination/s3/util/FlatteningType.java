/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

public enum FlatteningType {

    NO("No flattening"),
    ROOT_LEVEL("Root level flattening");
    private final String value;

    FlatteningType(final String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

}
