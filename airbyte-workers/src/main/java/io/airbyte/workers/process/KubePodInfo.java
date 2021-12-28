package io.airbyte.workers.process;

public record KubePodInfo(String namespace, String name) { }
