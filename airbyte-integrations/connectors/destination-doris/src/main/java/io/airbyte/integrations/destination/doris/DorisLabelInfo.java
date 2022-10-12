package io.airbyte.integrations.destination.doris;

import java.util.UUID;

public class DorisLabelInfo {

    private String prefix;

    private boolean enable2PC;

    public DorisLabelInfo(String labelPrefix, boolean enable2PC) {
        this.prefix = labelPrefix;
        this.enable2PC = enable2PC;
    }

    public String label() {
        return prefix + "_" + UUID.randomUUID() + System.currentTimeMillis() ;
    }

    public String label(long chkId) {
        return prefix + "_" + chkId;
    }

    public boolean isEnable2PC() {
        return enable2PC;
    }
}
