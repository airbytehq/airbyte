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

import com.alibaba.fastjson.JSON;
import io.airbyte.integrations.destination.starrocks.exception.StreamLoadFailException;
import io.airbyte.integrations.destination.starrocks.http.StreamLoadEntity;
import io.airbyte.integrations.destination.starrocks.stream.StreamLoadUtils;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

import org.apache.http.Header;
import org.apache.http.HttpEntity;
import org.apache.http.HttpHost;
import org.apache.http.HttpStatus;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.DefaultRedirectStrategy;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import javax.net.ssl.SSLContext;
import java.util.List;
import java.util.concurrent.TimeUnit;

import org.apache.http.conn.ssl.NoopHostnameVerifier;
import javax.net.ssl.SSLContext;

public class DefaultStreamLoader implements StreamLoader {

    private static final Logger LOG = LoggerFactory.getLogger(DefaultStreamLoader.class);

    private static final int ERROR_LOG_MAX_LENGTH = 3000;

    private final StreamLoadProperties properties;

    private final HttpClientBuilder clientBuilder;
    private final Header[] defaultHeaders;

    private final String loadUrlPath;

    private final String database;

    private final String loadTable;

    private volatile long availableHostPos;

    public DefaultStreamLoader(StreamLoadProperties properties) {
        this.properties = properties;
        this.database = properties.getDatabase();
        this.loadTable = properties.getTable();
        this.defaultHeaders = StreamLoadUtils.getHeaders(properties.getUser(), properties.getPassword());
        this.loadUrlPath = String.format(StarRocksConstants.PATTERN_PATH_STREAM_LOAD,
                database,
                loadTable);

        this.clientBuilder  = HttpClients.custom()
                .setRedirectStrategy(new DefaultRedirectStrategy() {
                    @Override
                    protected boolean isRedirectable(String method) {
                        return true;
                    }
                });
    }

    @Override
    public void close() {
        LOG.info("Finished stream load, database : {}, tmp table : {}",
                database, loadTable);
    }


    @Override
    public StreamLoadResponse send(List<AirbyteRecordMessage> records) throws Exception {
        String host = getAvailableHost();
        if (host == null) {
            throw new IOException("Could not find an available fe host.");
        }

        int port = properties.getHttpPort();
        String scheme = "http";
        // check if port for appropriate url scheme
        if (properties.getSSL()) {
            scheme = "https";
        }

        String sendUrl = String.format("%s://%s:%d%s", scheme, host, port, loadUrlPath);
        LOG.info("Stream Load URL : {}", sendUrl);

        String label = StreamLoadUtils.label(loadTable);
        HttpPut httpPut = new HttpPut(sendUrl);

        httpPut.setEntity(new StreamLoadEntity(records));
        httpPut.setHeaders(defaultHeaders);;
        httpPut.addHeader("label", label);

        LOG.info("Stream loading, label : {}, database : {}, table : {}, request : {}",
                label, database, loadTable, httpPut);

        String responseBody = null;

        try (CloseableHttpClient client = HttpClients.createDefault();) {
            long startNanoTime = System.nanoTime();
            try (CloseableHttpResponse response = client.execute(httpPut)) {
                HttpEntity responseEntity = response.getEntity();
                responseBody = EntityUtils.toString(responseEntity);
            }
            StreamLoadResponse streamLoadResponse = new StreamLoadResponse();
            StreamLoadResponse.StreamLoadResponseBody streamLoadBody
                    = JSON.parseObject(responseBody, StreamLoadResponse.StreamLoadResponseBody.class);
            streamLoadResponse.setBody(streamLoadBody);

            String status = streamLoadBody.getStatus();

            if (StarRocksConstants.RESULT_STATUS_SUCCESS.equals(status)
                    || StarRocksConstants.RESULT_STATUS_OK.equals(status)
                    || StarRocksConstants.RESULT_STATUS_TRANSACTION_PUBLISH_TIMEOUT.equals(status)) {
                streamLoadResponse.setCostNanoTime(System.nanoTime() - startNanoTime);
                LOG.info("Stream load completed, label : {}, database : {}, table : {}, body : {}",
                        label, database, loadTable, responseBody);

            } else if (StarRocksConstants.RESULT_STATUS_LABEL_EXISTED.equals(status)) {
                boolean succeed = checkLabelState(host, database, label);
                if (succeed) {
                    streamLoadResponse.setCostNanoTime(System.nanoTime() - startNanoTime);
                    LOG.info("Stream load completed, label : {}, database : {}, table : {}, body : {}",
                            label, database, loadTable, responseBody);
                } else {
                    String errorMsage = String.format("Stream load failed because label existed, " +
                            "db: %s, table: %s, label: %s", database, loadTable, label);
                    throw new StreamLoadFailException(errorMsage);
                }
            } else {
                String errorLog = getErrorLog(streamLoadBody.getErrorURL());
                String errorMsg = String.format("Stream load failed because of error, db: %s, table: %s, label: %s, " +
                                "\nresponseBody: %s\nerrorLog: %s", database, loadTable, label,
                        responseBody, errorLog);
                throw new StreamLoadFailException(errorMsg);
            }
            return streamLoadResponse;
        } catch (StreamLoadFailException e) {
            throw e;
        }  catch (Exception e) {
            LOG.error("error response from stream load: \n" + responseBody);
            String errorMsg = String.format("Stream load failed because of unknown exception, db: %s, table: %s, " +
                    "label: %s", database, loadTable, label);
            throw new StreamLoadFailException(errorMsg, e);
        }
    }

    protected String getAvailableHost() {
        String[] hosts = properties.getFeHost();
        int size = hosts.length;
        long pos = availableHostPos;
        while (pos < pos + size) {
            String host = hosts[(int) (pos % size)];
            if (testHttpConnection(host)) {
                pos++;
                availableHostPos = pos;
                return host;
            }
        }

        return null;
    }

    private boolean testHttpConnection(String host) {
        try {
            URL url = new URL(String.format("http://%s:%d", host, properties.getHttpPort()));
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(5000);
            connection.connect();
            connection.disconnect();
            return true;
        } catch (Exception e) {
            LOG.warn("Failed to connect to address:{}", host, e);
            return false;
        }
    }

    protected boolean checkLabelState(String host, String database, String label) throws Exception {
        int idx = 0;
        for (;;) {
            TimeUnit.SECONDS.sleep(Math.min(++idx, 5));
            try (CloseableHttpClient client = HttpClients.createDefault()) {
                String url = host + "/api/" + database + "/get_load_state?label=" + label;
                HttpGet httpGet = new HttpGet(url);
                httpGet.addHeader("Authorization",
                        StreamLoadUtils.getBasicAuthHeader(properties.getUser(), properties.getPassword()));
                httpGet.setHeader("Connection", "close");
                try (CloseableHttpResponse response = client.execute(httpGet)) {
                    String entityContent = EntityUtils.toString(response.getEntity());

                    if (response.getStatusLine().getStatusCode() != 200) {
                        throw new StreamLoadFailException("Failed to flush data to StarRocks, Error " +
                                "could not get the final state of label : `" + label + "`, body : " + entityContent);
                    }

                    LOG.info("Label `{}` check, body : {}", label, entityContent);
                    StreamLoadResponse.StreamLoadResponseBody responseBody =
                            JSON.parseObject(entityContent, StreamLoadResponse.StreamLoadResponseBody.class);
                    String state = responseBody.getState();
                    if (state == null) {
                        LOG.error("Get label state failed, body : {}", JSON.toJSONString(responseBody));
                        throw new StreamLoadFailException(String.format("Failed to flush data to StarRocks, Error " +
                                "could not get the final state of label[%s]. response[%s]\n", label, entityContent));
                    }
                    switch (state) {
                        case StarRocksConstants.LABEL_STATE_VISIBLE:
                        case StarRocksConstants.LABEL_STATE_PREPARED:
                        case StarRocksConstants.LABEL_STATE_COMMITTED:
                            return true;
                        case StarRocksConstants.LABEL_STATE_PREPARE:
                            continue;
                        case StarRocksConstants.LABEL_STATE_ABORTED:
                            return false;
                        case StarRocksConstants.LABEL_STATE_UNKNOWN:
                        default:
                            throw new StreamLoadFailException(String.format("Failed to flush data to StarRocks, Error " +
                                    "label[%s] state[%s]\n", label, state));
                    }
                }
            }
        }
    }

    protected String getErrorLog(String errorUrl) {
        if (errorUrl == null || !errorUrl.startsWith(HttpHost.DEFAULT_SCHEME_NAME)) {
            return null;
        }

        try (CloseableHttpClient httpclient = HttpClients.createDefault()) {
            HttpGet httpGet = new HttpGet(errorUrl);
            try (CloseableHttpResponse resp = httpclient.execute(httpGet)) {
                int code = resp.getStatusLine().getStatusCode();
                if (HttpStatus.SC_OK != code) {
                    LOG.warn("Request error log failed with error code: {}, errorUrl: {}", code, errorUrl);
                    return null;
                }

                HttpEntity respEntity = resp.getEntity();
                if (respEntity == null) {
                    LOG.warn("Request error log failed with null entity, errorUrl: {}", errorUrl);
                    return null;
                }
                String errorLog = EntityUtils.toString(respEntity);
                if (errorLog != null && errorLog.length() > ERROR_LOG_MAX_LENGTH) {
                    errorLog = errorLog.substring(0, ERROR_LOG_MAX_LENGTH);
                }
                return errorLog;
            }
        } catch (Exception e) {
            LOG.warn("Failed to get error log: {}.", errorUrl, e);
            return String.format("Failed to get error log: %s, exception message: %s", errorUrl, e.getMessage());
        }
    }

    protected String getSendUrl(String host, String database, String table) {
        if (host == null) {
            throw new IllegalArgumentException("None of the hosts in `load_url` could be connected.");
        }
        return host + "/api/" + database + "/" + table + "/_stream_load";
    }

}
