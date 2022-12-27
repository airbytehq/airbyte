/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb.utils;

public class StringUtils {
    public static boolean isNullOrWhitespaceOnly(String str) {
        if (str != null && str.length() != 0) {
            int len = str.length();

            for(int i = 0; i < len; ++i) {
                if (!Character.isWhitespace(str.charAt(i))) {
                    return false;
                }
            }

            return true;
        } else {
            return true;
        }
    }

}
