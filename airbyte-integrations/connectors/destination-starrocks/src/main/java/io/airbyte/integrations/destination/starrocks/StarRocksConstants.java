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

import java.nio.charset.StandardCharsets;

public interface StarRocksConstants {
    //connector config
    String KEY_USER = "username";
    String DEFAULT_USER = "root";
    String KEY_PWD = "password";
    String DEFAULT_PWD = "";
    String KEY_FE_HOST = "fe_host";
    String KEY_FE_HTTP_PORT = "http_port";
    int DEFAULT_FE_HTTP_PORT = 8030;
    String KEY_FE_QUERY_PORT = "query_port";
    int DEFAULT_FE_QUERY_PORT = 9030;
    String KEY_DB = "database";
    String DEFAULT_DB = "airbyte";
    String KEY_TABLE = "table";

    //jdbc
    String JDBC_DRIVER = "com.mysql.jdbc.Driver";
    String CJ_JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";
    String PATTERN_JDBC_URL = "jdbc:mysql://%s:%d/%s?rewriteBatchedStatements=true&useUnicode=true&characterEncoding=utf8";


    //stream load
    String PATTERN_PATH_STREAM_LOAD = "/api/%s/%s/_stream_load";

    String PATH_TRANSACTION_BEGIN = "/api/transaction/begin";
    String PATH_TRANSACTION_SEND = "/api/transaction/load";
    String PATH_TRANSACTION_ROLLBACK = "/api/transaction/rollback";
    String PATH_TRANSACTION_PRE_COMMIT = "/api/transaction/prepare";
    String PATH_TRANSACTION_COMMIT = "/api/transaction/commit";

    String PATH_STREAM_LOAD_STATE = "/api/{db}/get_load_state?label={label}";

    String RESULT_STATUS_OK = "OK";
    String RESULT_STATUS_SUCCESS = "Success";
    String RESULT_STATUS_FAILED = "Fail";
    String RESULT_STATUS_LABEL_EXISTED = "Label Already Exists";
    String RESULT_STATUS_TRANSACTION_NOT_EXISTED = "TXN_NOT_EXISTS";
    String RESULT_STATUS_TRANSACTION_COMMIT_TIMEOUT = "Commit Timeout";
    String RESULT_STATUS_TRANSACTION_PUBLISH_TIMEOUT = "Publish Timeout";

    String LABEL_STATE_VISIBLE = "VISIBLE";
    String LABEL_STATE_COMMITTED = "COMMITTED";
    String LABEL_STATE_PREPARED = "PREPARED";
    String LABEL_STATE_PREPARE = "PREPARE";
    String LABEL_STATE_ABORTED = "ABORTED";
    String LABEL_STATE_UNKNOWN = "UNKNOWN";

    //csv
    interface CsvFormat {
        String LINE_DELIMITER = "\\x02";
        byte[] LINE_DELIMITER_BYTE = StarRocksDelimiterParser.parse(LINE_DELIMITER).getBytes(StandardCharsets.UTF_8);

        String COLUMN_DELIMITER = "\\x01";
        byte[] COLUMN_DELIMITER_BYTE = StarRocksDelimiterParser.parse(COLUMN_DELIMITER).getBytes(StandardCharsets.UTF_8);

        String LINE_PATTERN = "%s" + StarRocksDelimiterParser.parse(COLUMN_DELIMITER)
            + "%d" + StarRocksDelimiterParser.parse(COLUMN_DELIMITER)
            + "%s" + StarRocksDelimiterParser.parse(LINE_DELIMITER);
    }

}
