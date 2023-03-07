import { fetchDocumentation } from "./Documentation";

describe("fetchDocumentation", () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  it("should throw on non markdown content-type", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      Headers: new Headers([["Content-Type", "text/html; charset=utf-8"]]),
    });
    await expect(fetchDocumentation("/docs/integrations/destinations/firestore.md")).rejects.toThrow();
  });
});
