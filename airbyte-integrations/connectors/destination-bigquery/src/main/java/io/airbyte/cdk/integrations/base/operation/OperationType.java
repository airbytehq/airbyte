package io.airbyte.cdk.integrations.base.operation;

public enum OperationType {
    SPEC,
    CHECK,
    DISCOVER,
    READ,
    WRITE;
}
