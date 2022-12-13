import {
  getPostgresCreateSourceBody,
  requestCreateSource,
  requestDeleteSource,
  requestWorkspaceId,
} from "commands/request";
import { initialSetupCompleted } from "commands/workspaces";

describe("Auto-detect schema changes", () => {
  beforeEach(() => {
    initialSetupCompleted();
    requestWorkspaceId();
  });

  it("creates a source", () => {
    const payload = getPostgresCreateSourceBody("Test source");
    let sourceId: string;
    console.log("payload", payload);

    requestCreateSource("Test source", payload).then((response) => {
      sourceId = response.sourceId;
      expect(sourceId).to.be.a("string");

      requestDeleteSource(sourceId);
    });
  });
});
