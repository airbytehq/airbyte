/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package io.airbyte.integrations.destination.starrocks;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import org.joda.time.DateTime;

public class StarRocksWriteConfig {
    private final StreamLoadProperties streamLoadProperties;

    private final String streamName;
    private final String namespace;
    private final String database;
    private final String tmpTableName;
    private final String outputTableName;
    private final DestinationSyncMode syncMode;
    private final DateTime writeDatetime;

    private final StreamLoader streamLoader;

    public StarRocksWriteConfig(Builder builder) {
        this.streamLoadProperties = builder.streamLoadProperties;

        this.streamName = builder.streamName;
        this.namespace = builder.namespace;
        this.database = builder.database;
        this.tmpTableName = builder.tmpTableName;
        this.outputTableName = builder.outputTableName;
        this.syncMode = builder.syncMode;
        this.writeDatetime = builder.writeDatetime;

        this.streamLoader = builder.streamLoader;
    }

    public StreamLoadProperties getStreamLoadProperties() {
        return streamLoadProperties;
    }

    public String getStreamName() {
        return streamName;
    }

    public String getNamespace() {
        return namespace;
    }

    public String getTmpTableName() {
        return tmpTableName;
    }

    public String getDatabase() {
        return database;
    }

    public String getOutputTableName() {
        return outputTableName;
    }

    public DestinationSyncMode getSyncMode() {
        return syncMode;
    }

    public DateTime getWriteDatetime() {
        return writeDatetime;
    }

    public StreamLoader getStreamLoader() {
        return streamLoader;
    }

    public boolean useTmpTable() {
        return this.syncMode == DestinationSyncMode.OVERWRITE;
    }

    public static Builder builder() {
        return new Builder();
    }

    @Override
    public String toString() {
        return "StarRocksWriteConfig{" +
                "streamName=" + streamName +
                ", namespace=" + namespace +
                ", database=" + database +
                ", tmpTableName=" + tmpTableName +
                ", outputTableName=" + outputTableName +
                ", syncMode=" + syncMode +
                '}';
    }


    public static class Builder {
        private StreamLoadProperties streamLoadProperties;

        private String streamName;
        private String namespace;
        private String database;
        private String tmpTableName;
        private String outputTableName;
        private DestinationSyncMode syncMode;
        private DateTime writeDatetime;

        private StreamLoader streamLoader;

        public Builder streamLoadProperties(StreamLoadProperties streamLoadProperties) {
            this.streamLoadProperties = streamLoadProperties;
            return this;
        }

        public Builder streamName(String streamName) {
            this.streamName = streamName;
            return this;
        }
        public Builder namespace(String namespace) {
            this.namespace = namespace;
            return this;
        }
        public Builder database(String database) {
            this.database = database;
            return this;
        }
        public Builder tmpTableName(String tmpTableName) {
            this.tmpTableName = tmpTableName;
            return this;
        }
        public Builder outputTableName(String outputTableName) {
            this.outputTableName = outputTableName;
            return this;
        }
        public Builder syncMode(DestinationSyncMode syncMode) {
            this.syncMode = syncMode;
            return this;
        }
        public Builder writeDatetime(DateTime writeDatetime) {
            this.writeDatetime = writeDatetime;
            return this;
        }

        public Builder streamLoader(StreamLoader streamLoader) {
            this.streamLoader = streamLoader;
            return this;
        }

        public StarRocksWriteConfig build() {
            StarRocksWriteConfig starRocksWriteConfig = new StarRocksWriteConfig(this);
            Preconditions.checkNotNull(syncMode, "Undefined destination sync mode");
            Preconditions.checkNotNull(streamLoader, "streamLoader is null.");

            return starRocksWriteConfig;
        }
    }

}
