package io.airbyte.integrations.base.destination.typing_deduping;

public interface TyperDeduper {

  void prepareFinalTables() throws Exception;
  void typeAndDedupe(String originalNamespace, String originalName) throws Exception;
  void commitFinalTables() throws Exception;
}
