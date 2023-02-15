/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class BaseResponse<T> {
    private int code;
    private String msg;
    private T data;
    private int count;

    public BaseResponse(int code, String msg, T data, int count) {
        this.code = code;
        this.msg = msg;
        this.data = data;
        this.count = count;
    }

    public int getCode() {
        return code;
    }

    public String getMsg() {
        return msg;
    }

    public T getData(){
        return data;
    }

    public int getCount() {
        return count;
    }

}
