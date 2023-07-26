// Copyright 2021-present StarRocks, Inc. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package io.airbyte.integrations.destination.starrocks;

public class StreamLoadProperties {
    private String database;
    private String table;
    private String[] feHost;
    private int httpPort;
    private int queryPort;
    private String user;
    private String password;
    private boolean ssl;

    public StreamLoadProperties(String database, String table, String[] feHost, int httpPort, String user, String password, int queryPort, boolean ssl) {
        this.database = database;
        this.table = table;
        this.feHost = feHost;
        this.httpPort = httpPort;
        this.user = user;
        this.password = password;
        this.queryPort = queryPort;
        this.ssl = ssl;
    }

    public String getDatabase() {
        return database;
    }

    public String getTable() {
        return table;
    }

    public String[] getFeHost() {
        return feHost;
    }

    public int getHttpPort() {
        return httpPort;
    }

    public String getUser() {
        return user;
    }

    public String getPassword() {
        return password;
    }

    public int getQueryPort() {
        return queryPort;
    }

    public boolean getSSL() {
        return ssl;
    }
}
