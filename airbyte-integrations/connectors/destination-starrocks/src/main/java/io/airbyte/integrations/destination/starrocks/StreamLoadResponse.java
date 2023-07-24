/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
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

import java.io.Serializable;

public class StreamLoadResponse implements Serializable {

    private boolean cancel;

    private Long flushRows;
    private Long flushBytes;
    private Long costNanoTime;

    private StreamLoadResponseBody body;
    private Exception exception;

    public void cancel() {
        this.cancel = true;
    }

    public boolean isCancel() {
        return cancel;
    }

    public Long getFlushRows() {
        return flushRows;
    }

    public Long getFlushBytes() {
        return flushBytes;
    }

    public Long getCostNanoTime() {
        return costNanoTime;
    }

    public StreamLoadResponseBody getBody() {
        return body;
    }

    public Exception getException() {
        return exception;
    }

    public void setFlushBytes(long flushBytes) {
        this.flushBytes = flushBytes;
    }

    public void setFlushRows(long flushRows) {
        this.flushRows = flushRows;
    }

    public void setCostNanoTime(long costNanoTime) {
        this.costNanoTime = costNanoTime;
    }

    public void setBody(StreamLoadResponseBody body) {
        this.body = body;
    }

    public void setException(Exception e) {
        this.exception = e;
    }

    public static class StreamLoadResponseBody implements Serializable {
        private Long txnId;
        private String label;
        private String state;
        private String status;
        private String existingJobStatus;
        private String message;
        private String msg;
        private Long numberTotalRows;
        private Long numberLoadedRows;
        private Long numberFilteredRows;
        private Long numberUnselectedRows;
        private String errorURL;
        private Long loadBytes;
        private Long loadTimeMs;
        private Long beginTxnTimeMs;
        private Long streamLoadPlanTimeMs;
        private Long readDataTimeMs;
        private Long writeDataTimeMs;
        private Long commitAndPublishTimeMs;

        public Long getNumberTotalRows() {
            return numberTotalRows;
        }

        public Long getNumberLoadedRows() {
            return numberLoadedRows;
        }

        public void setTxnId(Long txnId) {
            this.txnId = txnId;
        }

        public void setLabel(String label) {
            this.label = label;
        }

        public void setState(String state) {
            this.state = state;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public void setExistingJobStatus(String existingJobStatus) {
            this.existingJobStatus = existingJobStatus;
        }

        public void setMessage(String message) {
            this.message = message;
        }

        public void setMsg(String msg) {
            this.msg = msg;
        }

        public void setNumberTotalRows(Long numberTotalRows) {
            this.numberTotalRows = numberTotalRows;
        }

        public void setNumberLoadedRows(Long numberLoadedRows) {
            this.numberLoadedRows = numberLoadedRows;
        }

        public void setNumberFilteredRows(Long numberFilteredRows) {
            this.numberFilteredRows = numberFilteredRows;
        }

        public void setNumberUnselectedRows(Long numberUnselectedRows) {
            this.numberUnselectedRows = numberUnselectedRows;
        }

        public void setErrorURL(String errorURL) {
            this.errorURL = errorURL;
        }

        public void setLoadBytes(Long loadBytes) {
            this.loadBytes = loadBytes;
        }

        public void setLoadTimeMs(Long loadTimeMs) {
            this.loadTimeMs = loadTimeMs;
        }

        public void setBeginTxnTimeMs(Long beginTxnTimeMs) {
            this.beginTxnTimeMs = beginTxnTimeMs;
        }

        public void setStreamLoadPlanTimeMs(Long streamLoadPlanTimeMs) {
            this.streamLoadPlanTimeMs = streamLoadPlanTimeMs;
        }

        public void setReadDataTimeMs(Long readDataTimeMs) {
            this.readDataTimeMs = readDataTimeMs;
        }

        public void setWriteDataTimeMs(Long writeDataTimeMs) {
            this.writeDataTimeMs = writeDataTimeMs;
        }

        public void setCommitAndPublishTimeMs(Long commitAndPublishTimeMs) {
            this.commitAndPublishTimeMs = commitAndPublishTimeMs;
        }

        public String getState() {
            return state;
        }

        public String getStatus() {
            return status;
        }

        public String getMsg() {
            return msg;
        }

        public Long getCommitAndPublishTimeMs() {
            return commitAndPublishTimeMs;
        }

        public Long getStreamLoadPlanTimeMs() {
            return streamLoadPlanTimeMs;
        }

        public Long getReadDataTimeMs() {
            return readDataTimeMs;
        }

        public Long getWriteDataTimeMs() {
            return writeDataTimeMs;
        }

        public Long getLoadTimeMs() {
            return loadTimeMs;
        }

        public Long getNumberFilteredRows() {
            return numberFilteredRows;
        }

        public String getErrorURL() {
            return errorURL;
        }
    }
}
