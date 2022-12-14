import {
  getPostgresCreateSourceBody,
  requestCreateSource,
  requestDeleteSource,
  requestWorkspaceId,
} from "commands/api";
import { initialSetupCompleted } from "commands/workspaces";

describe("Auto-detect schema changes", () => {
  beforeEach(() => {
    initialSetupCompleted();
    requestWorkspaceId();
  });

  it("creates a source", async () => {
    const payload = getPostgresCreateSourceBody("Test source");

    const { sourceId } = await requestCreateSource("Test source", payload);

    expect(sourceId).to.be.a("string");
    requestDeleteSource(sourceId);
  });
});
