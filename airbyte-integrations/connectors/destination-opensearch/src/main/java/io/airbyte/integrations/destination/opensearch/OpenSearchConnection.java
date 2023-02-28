/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

import org.opensearch.client.Node;
import org.opensearch.client.RestClient;
import org.opensearch.client.RestClientBuilder;
import org.opensearch.client.json.jackson.JacksonJsonpMapper;
import org.opensearch.client.opensearch.OpenSearchClient;
import org.opensearch.client.opensearch._types.OpenSearchException;
import org.opensearch.client.opensearch._types.Refresh;
import org.opensearch.client.opensearch.cat.indices.IndicesRecord;
import org.opensearch.client.opensearch.core.BulkRequest;
import org.opensearch.client.opensearch.core.BulkResponse;
import org.opensearch.client.opensearch.core.CreateResponse;
import org.opensearch.client.opensearch.core.SearchResponse;
import org.opensearch.client.opensearch.core.bulk.BulkOperation;
import org.opensearch.client.opensearch.core.bulk.CreateOperation;
import org.opensearch.client.opensearch.core.search.Hit;
import org.opensearch.client.opensearch.core.search.HitsMetadata;
import org.opensearch.client.opensearch.indices.*;
import com.fasterxml.jackson.core.JsonPointer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.db.util.SSLCertificateUtils;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;

import org.apache.http.Header;
import org.apache.http.HttpHost;
import org.apache.http.message.BasicHeader;
import org.opensearch.client.transport.OpenSearchTransport;
import org.opensearch.client.transport.endpoints.BooleanResponse;
import org.opensearch.client.transport.rest_client.RestClientTransport;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 * All communication with OpenSearch should be done through this class.
 */
public class OpenSearchConnection {

    // this is the max number of hits we can query without paging
    private static final int MAX_HITS = 10000;
    private static Logger log = LoggerFactory.getLogger(OpenSearchConnection.class);

    private final OpenSearchClient client;
    private final RestClient restClient;
    private final HttpHost httpHost;
    private final ObjectMapper mapper = new ObjectMapper();

    /**
     * Creates a new OpenSearchConnection that can be used to read/write records to indices
     *
     * @param config Configuration parameters for connecting to the OpenSearch host
     */
    public OpenSearchConnection(ConnectorConfiguration config) {
        log.info(String.format("creating OpensearchConnection: %s", config.getEndpoint()));

        // Create the low-level client
        httpHost = HttpHost.create(config.getEndpoint());
        final RestClientBuilder builder = RestClient.builder(httpHost);

        // Set custom user's certificate if provided
        if (config.getCaCertificate() != null && !config.getCaCertificate().isEmpty()) {
            builder.setHttpClientConfigCallback(clientBuilder -> {
                clientBuilder.setSSLContext(SSLCertificateUtils.createContextFromCaCert(config.getCaCertificate()));
                return clientBuilder;
            });
        }

        restClient = builder
                .setDefaultHeaders(configureHeaders(config))
                .setFailureListener(new FailureListener())
                .build();
        // Create the transport that provides JSON and http services to API clients
        OpenSearchTransport transport = new RestClientTransport(restClient, new JacksonJsonpMapper());
        // And create our API client
        client = new OpenSearchClient(transport);
    }

    static class FailureListener extends RestClient.FailureListener {

        @Override
        public void onFailure(Node node) {
            log.error("RestClient failure: {}", node);
        }

    }

    /**
     * Configures the default headers for requests to the OpenSearch server
     *
     * @param config connection information
     * @return the default headers
     */
    protected Header[] configureHeaders(ConnectorConfiguration config) {
        final var headerList = new ArrayList<Header>();
        // add Authorization header if credentials are present
        final var auth = config.getAuthenticationMethod();
        switch (auth.getMethod()) {
            case secret -> {
                var bytes = (auth.getApiKeyId() + ":" + auth.getApiKeySecret()).getBytes(StandardCharsets.UTF_8);
                var header = "ApiKey " + Base64.getEncoder().encodeToString(bytes);
                headerList.add(new BasicHeader("Authorization", header));
            }
            case basic -> {
                var basicBytes = (auth.getUsername() + ":" + auth.getPassword()).getBytes(StandardCharsets.UTF_8);
                var basicHeader = "Basic " + Base64.getEncoder().encodeToString(basicBytes);
                headerList.add(new BasicHeader("Authorization", basicHeader));
            }
        }
        return headerList.toArray(new Header[0]);
    }

    /**
     * Pings the OpenSearch server for "up" check, and configuration validation
     *
     * @return true if connection was successful
     */
    public boolean checkConnection() {
        log.info("checking openSearch connection");
        try {
            final var info = client.info();
            log.info("checked openSearch connection: {}, version: {}", info.clusterName(), info.version());
            return true;
        } catch (Exception e) {
            log.error("unknown exception while pinging openSearch server", e);
            return false;
        }
    }

    /**
     * Writes a single record to the OpenSearch server
     *
     * @param index The index to write the record to
     * @param id    The ID to give the new document
     * @param data  The body of the document (source record)
     * @return results of the create operation
     * @throws Exception if an error is encountered
     */
    public CreateResponse createDocument(String index, String id, JsonNode data) throws Exception {
        CreateResponse createResponse = client.create(builder -> builder.id(id).document(data).index(index));
        log.debug("wrote record: {}", createResponse.result());
        return createResponse;
    }

    /**
     * Bulk operation to append multiple documents to an OpenSearch server
     *
     * @param index   The index to add the documents to
     * @param records The collection of records to create documents from
     * @return the response of the bulk operation
     * @throws IOException if there is server connection problem, or a non-successful operation on the
     *                     server
     */
    public BulkResponse indexDocuments(String index, List<AirbyteRecordMessage> records, OpenSearchWriteConfig config) throws IOException {
        var bulkRequest = new BulkRequest.Builder();
        for (var doc : records) {
            log.debug("adding record to bulk create: {}", doc.getData());
            var bulkOperation = new BulkOperation.Builder();
            bulkOperation
                .index(c -> c.index(index).id(extractPrimaryKey(doc, config))
                .document(doc.getData()));
            bulkRequest.operations(bulkOperation.build()).refresh(Refresh.True);

        }

        try {
            return client.bulk(b -> bulkRequest);
        } catch (Exception e) {
            throw unwrappedApiException("failed write operation", e);
        }
    }

    private String extractPrimaryKey(AirbyteRecordMessage doc, OpenSearchWriteConfig config) {
        if (!config.hasPrimaryKey()) {
            return UUID.randomUUID().toString();
        }
        var optFirst = config.getPrimaryKey().stream().findFirst();
        StringBuilder sb = new StringBuilder();
        if (optFirst.isPresent()) {
            log.debug("trying to extract primary key using {}", optFirst.get());
            optFirst.get().forEach(s -> sb.append(String.format("/%s", s)));
        }
        if (sb.length() > 0) {
            JsonPointer ptr = JsonPointer.valueOf(sb.toString());
            var pkNode = doc.getData().at(ptr);
            if (!pkNode.isMissingNode() && pkNode.isValueNode()) {
                return pkNode.asText();
            }
        }
        log.warn("unable to extract primary key");
        return UUID.randomUUID().toString();
    }

    /**
     * returns the first 10k documents of a given index
     *
     * @param index the index to search
     * @return a list of matching documents
     * @throws IOException if there is server communication error, or invalid index
     */
    public List<JsonNode> getRecords(String index) throws IOException {
        log.info("getting records for index: {}", index);
        SearchResponse<JsonNode> search = client.search(s -> s.index(index).size(MAX_HITS), JsonNode.class);
        HitsMetadata<JsonNode> hitMeta = search.hits();
        return hitMeta.hits().stream().map(Hit::source).collect(Collectors.toList());
    }

    /**
     * Shutdown the connection to the OpenSearch server
     */
    public void close() throws IOException {
        this.restClient.close();
        this.client.shutdown();
    }

    public List<String> allIndices() {
        try {
            var response = client.cat().indices(r -> r);
            return response.valueBody().stream().map(IndicesRecord::index).collect(Collectors.toList());
        } catch (IOException e) {
            log.error("unknown exception while getting indices", e);
        }
        return new ArrayList<>();
    }

    /**
     * Creates an index on OpenSearch if it's missing
     *
     * @param index the index name to create
     */
    public void createIndexIfMissing(String index) {
        try {
            BooleanResponse existsResponse = client.indices().exists(b -> b.index(index));
            if (existsResponse.value()) {
                log.info("index exists: {}", index);
                return;
            }
            log.info("creating index: {}, info: {}", index, client.info());
            final CreateIndexResponse createIndexResponse = client.indices().create(b -> b.index(index));
            if (Boolean.TRUE.equals(createIndexResponse.acknowledged()) && createIndexResponse.shardsAcknowledged()) {
                log.info("created index: {}", index);
            } else {
                log.info("did not create index: {}, {}", index, mapper.writeValueAsString(createIndexResponse));
            }
        } catch (IOException e) {
            log.warn("unknown exception while creating index", e);
        }
    }

    /**
     * Deletes an index if present, suppressing any exceptions
     *
     * @param indexName The index to delete
     */
    public void deleteIndexIfPresent(String indexName) {
        try {
            var exists = client.indices().exists(b -> b.index(indexName));
            if (exists.value()) {
                client.indices().delete(b -> b.index(indexName));
            }
        } catch (IOException e) {
            log.warn("unknown exception while deleting index", e);
        }
    }

    /**
     * Clones a source index to a destination index. If the destination index already exists, it deletes
     * it before cloning
     *
     * @param sourceIndexName      The index to clone
     * @param destinationIndexName The destination index name to clone to.
     */
    public void replaceIndex(String sourceIndexName, String destinationIndexName) {
        log.info("replacing index: {}, with index: {}", destinationIndexName, sourceIndexName);
        try {
            var sourceExists = client.indices().exists(i -> i.index(sourceIndexName));
            if (!sourceExists.value()) {
                throw new RuntimeException(
                        String.format("the source index does not exist. unable to replace the destination index. source: %s, destination: %s", sourceIndexName,
                                destinationIndexName));
            }

            // delete the destination if it exists
            var destinationExists = client.indices().exists(i -> i.index(destinationIndexName));
            if (destinationExists.value()) {
                log.warn("deleting existing index: {}", destinationIndexName);
                deleteIndexIfPresent(destinationIndexName);
            }

            client.indices().putSettings(b -> b.index(sourceIndexName).settings(s -> s.blocks(w -> w.write(true))));

            // clone to the destination
            client.indices().clone(c -> c.index(sourceIndexName).target(destinationIndexName));

            // enable writing on new index
            client.indices().putSettings(b -> b.index(destinationIndexName).settings(s -> s.blocks(w -> w.write(false))));
        } catch (IOException e) {
            throw new RuntimeException("unknown exception while replacing index", e);
        }
    }

    /**
     * Unwraps a rest client ApiException, so we can log the details
     *
     * @param message message to add to the log entry
     * @param e       source ApiException
     * @return a new RuntimeException with the ApiException as the source
     */
    private RuntimeException unwrappedApiException(String message, Exception e) {
        log.error(message);
        if (Objects.isNull(e) || Objects.isNull(e.getCause())) {
            log.error("unknown ApiException");
            return new RuntimeException(e);
        }
        if (OpenSearchException.class.isAssignableFrom(e.getCause().getClass())) {
            OpenSearchException esException = ((OpenSearchException) e.getCause());
            String errorMessage = String.format("OpensearchError: status:%s, error:%s", esException.status(), esException.error().toString());
            return new RuntimeException(errorMessage);
        }
        return new RuntimeException(e);
    }

}
