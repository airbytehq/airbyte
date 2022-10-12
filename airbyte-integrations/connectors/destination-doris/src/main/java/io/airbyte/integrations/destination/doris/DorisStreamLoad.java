package io.airbyte.integrations.destination.doris;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.destination.doris.exception.DorisRuntimeException;
import io.airbyte.integrations.destination.doris.exception.StreamLoadException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.entity.InputStreamEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.util.EntityUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.Future;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DorisStreamLoad {


    private static final Logger LOG = LoggerFactory.getLogger(DorisStreamLoad.class);
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    public static final Pattern LABEL_EXIST_PATTERN =
            Pattern.compile("errCode = 2, detailMessage = Label \\[(.*)\\] " +
                    "has already been used, relate to txn \\[(\\d+)\\]");
    public static final Pattern COMMITTED_PATTERN =
            Pattern.compile("errCode = 2, detailMessage = transaction \\[(\\d+)\\] " +
                    "is already \\b(COMMITTED|committed|VISIBLE|visible)\\b, not pre-committed.");
    private final DorisLabelInfo dorisLabelInfo;
    private final byte[] lineDelimiter;
    private static final String LOAD_FIRST_URL_PATTERN = "http://%s/api/%s/%s/_stream_load";
    private static final String LOAD_SECOND_URL_PATTERN = "http://%s/api/%s/_stream_load_2pc";
    private static final String LINE_DELIMITER_DEFAULT = "\n";
    public static final String CSV_COLUMN_SEPARATOR = "\t";



    private final String hostPort;
    private final String loadUrlStr;
    private final String secondUrlStr;
    private final String user;
    private final String passwd;
    private final String db;
    private final boolean enable2PC;
    private final Properties streamLoadProp;
    private final Integer maxRetry;
    private Long txnID = 0L;


    private Path path;

    private Future<CloseableHttpResponse> pendingLoadFuture;
    private final CloseableHttpClient httpClient;

    public static final String SUCCESS = "Success";
    public static final String PUBLISH_TIMEOUT = "Publish Timeout";
    private static final List<String> DORIS_SUCCESS_STATUS = new ArrayList<>(Arrays.asList(SUCCESS, PUBLISH_TIMEOUT));

    private static final String JOB_EXIST_FINISHED = "FINISHED";

    public static final String LABEL_ALREADY_EXIST = "Label Already Exists";
    public static final String FAIL = "Fail";


    public DorisStreamLoad(
            Path path,
            DorisConnectionOptions dorisOptions,
            DorisLabelInfo dorisLabelInfo,
            CloseableHttpClient httpClient,
            List<String> head
            ) {
        this.hostPort = dorisOptions.getHostPort();
        this.db = dorisOptions.getDb();
        this.user = dorisOptions.getUser();
        this.passwd = dorisOptions.getPwd();
        this.dorisLabelInfo = dorisLabelInfo;
        this.loadUrlStr = String.format(LOAD_FIRST_URL_PATTERN, hostPort, db, dorisOptions.getTable());
        this.secondUrlStr = String.format(LOAD_SECOND_URL_PATTERN, hostPort, db);
        this.enable2PC = true;


        StringBuilder stringBuilder = new StringBuilder();
        for (String s : head) {
            if (!stringBuilder.isEmpty()) stringBuilder.append(",");
            stringBuilder.append(s);
        }
        this.streamLoadProp = new Properties();
        streamLoadProp.setProperty("column_separator",CSV_COLUMN_SEPARATOR);
        streamLoadProp.setProperty("columns",stringBuilder.toString());

        this.maxRetry = 3;
        this.path = path;
        this.httpClient = httpClient;

        lineDelimiter = LINE_DELIMITER_DEFAULT.getBytes(StandardCharsets.UTF_8);
    }

    public Long getTxnID() {
        return txnID;
    }

    public void firstCommit() throws Exception {
        Path pathChecked = Preconditions.checkNotNull(path,"stream load temp CSV file is empty.");
        String label = dorisLabelInfo.label();
        LOG.info("preCommit label {}. .", label);
        StreamLoadRespContent respContent = null;
        try {

            InputStreamEntity entity = new InputStreamEntity( new FileInputStream(pathChecked.toFile()));
            StreamLoadHttpPutBuilder builder = StreamLoadHttpPutBuilder.builder();
            builder.setUrl(loadUrlStr)
                    .baseAuth(user, passwd)
                    .addCommonHeader()
                    .enable2PC(enable2PC)
                    .setLabel(label)
                    .setEntity(entity)
                    .addProperties(streamLoadProp);
            HttpPut build = builder.build();
            respContent = handlePreCommitResponse(httpClient.execute(build));
            Preconditions.checkState("true".equals(respContent.getTwoPhaseCommit()));
            if (!DORIS_SUCCESS_STATUS.contains(respContent.getStatus())) {
                String errMsg = String.format("stream load error: %s, see more in %s", respContent.getMessage(), respContent.getErrorURL());
                throw new DorisRuntimeException(errMsg);
            }
        } catch (Exception e) {
            LOG.warn("failed to stream load data", e);
            throw e;
        }

        String commitType = enable2PC ? "preCommit" : "commit";
        LOG.info("{} for label {} finished", commitType, label);
        this.txnID = respContent.getTxnId();
    }


    //commit
    public void commitTransaction() throws IOException {
        int statusCode = -1;
        String reasonPhrase = null;
        int retry = 0;
        CloseableHttpResponse response = null;
        StreamLoadHttpPutBuilder putBuilder = StreamLoadHttpPutBuilder.builder();
        putBuilder.setUrl(secondUrlStr)
                .baseAuth(user, passwd)
                .addCommonHeader()
                .addTxnId(txnID)
                .setEmptyEntity()
                .commit();
        while (retry++ < maxRetry) {

            try {
                response = httpClient.execute(putBuilder.build());
            } catch (IOException e) {
                continue;
            }
            statusCode = response.getStatusLine().getStatusCode();
            reasonPhrase = response.getStatusLine().getReasonPhrase();
            if (statusCode != 200) {
                LOG.warn("commit failed with {}, reason {}", hostPort, reasonPhrase);
            } else {
                break;
            }
        }

        if (statusCode != 200) {
            throw new DorisRuntimeException("stream load error: " + reasonPhrase);
        }

        ObjectMapper mapper = new ObjectMapper();
        if (response.getEntity() != null) {
            String loadResult = EntityUtils.toString(response.getEntity());
            Map<String, String> res = mapper.readValue(loadResult, new TypeReference<HashMap<String, String>>() {
            });
            Matcher matcher  = LABEL_EXIST_PATTERN.matcher(res.get("msg"));
            if (res.get("status").equals(FAIL) && !matcher.matches()) {
                throw new DorisRuntimeException("Commit failed " + loadResult);
            } else {
                LOG.info("load result {}", loadResult);
            }
        }
    }


    //abort
    public void abortTransaction() throws Exception {
        StreamLoadHttpPutBuilder builder = StreamLoadHttpPutBuilder.builder();
        builder.setUrl(secondUrlStr)
                .baseAuth(user, passwd)
                .addCommonHeader()
                .addTxnId(txnID)
                .setEmptyEntity()
                .abort();
        CloseableHttpResponse response = httpClient.execute(builder.build());

        int statusCode = response.getStatusLine().getStatusCode();
        if (statusCode != 200 || response.getEntity() == null) {
            LOG.warn("abort transaction response: " + response.getStatusLine().toString());
            throw new DorisRuntimeException("Failed abort transaction:" + txnID + ", with url " + secondUrlStr);
        }

        ObjectMapper mapper = new ObjectMapper();
        String loadResult = EntityUtils.toString(response.getEntity());
        Map<String, String> res = mapper.readValue(loadResult, new TypeReference<HashMap<String, String>>(){});
        if (FAIL.equals(res.get("status"))) {
            LOG.warn("Fail to abort transaction. error: {}", res.get("msg"));
        }
    }






    private StreamLoadRespContent stopLoad() throws IOException {
        LOG.info("stream load stopped.");
        Preconditions.checkState(pendingLoadFuture != null);
        try {
            return handlePreCommitResponse(pendingLoadFuture.get());
        } catch (Exception e) {
            throw new DorisRuntimeException(e);
        }
    }






//    public Future<CloseableHttpResponse> getPendingLoadFuture() {
//        return pendingLoadFuture;
//    }

    public StreamLoadRespContent handlePreCommitResponse(CloseableHttpResponse response) throws Exception{
        final int statusCode = response.getStatusLine().getStatusCode();
        if (statusCode == 200 && response.getEntity() != null) {
            String loadResult = EntityUtils.toString(response.getEntity());
            LOG.info("load Result {}", loadResult);
            return OBJECT_MAPPER.readValue(loadResult, StreamLoadRespContent.class);
        }
        throw new StreamLoadException("stream load response error: " + response.getStatusLine().toString());
    }


    public void close() throws IOException {
        if (null != httpClient) {
            try {
                httpClient.close();
            } catch (IOException e) {
                throw new IOException("Closing httpClient failed.", e);
            }
        }
    }





}
