import { AnalyticsService } from "./AnalyticsService";
import { Action, Namespace } from "./types";

describe("AnalyticsService", () => {
  beforeEach(() => {
    window.analytics = {
      track: jest.fn(),
      alias: jest.fn(),
      group: jest.fn(),
      identify: jest.fn(),
      page: jest.fn(),
      reset: jest.fn(),
      user: jest.fn(),
      setAnonymousId: jest.fn(),
      init: jest.fn(),
      use: jest.fn(),
      addIntegration: jest.fn(),
      load: jest.fn(),
      trackLink: jest.fn(),
      trackForm: jest.fn(),
      ready: jest.fn(),
      debug: jest.fn(),
      on: jest.fn(),
      timeout: jest.fn(),
    };
  });

  it("should send events to segment", () => {
    const service = new AnalyticsService();
    service.track(Namespace.CONNECTION, Action.CREATE, {});
    expect(window.analytics.track).toHaveBeenCalledWith("Airbyte.UI.Connection.Create", expect.anything());
  });

  it("should send version and environment for prod", () => {
    const service = new AnalyticsService("0.42.13");
    service.track(Namespace.CONNECTION, Action.CREATE, {});
    expect(window.analytics.track).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ environment: "prod", airbyte_version: "0.42.13" })
    );
  });

  it("should send version and environment for dev", () => {
    const service = new AnalyticsService("dev");
    service.track(Namespace.CONNECTION, Action.CREATE, {});
    expect(window.analytics.track).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ environment: "dev", airbyte_version: "dev" })
    );
  });

  it("should pass parameters to segment event", () => {
    const service = new AnalyticsService();
    service.track(Namespace.CONNECTION, Action.CREATE, { actionDescription: "Created new connection" });
    expect(window.analytics.track).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ actionDescription: "Created new connection" })
    );
  });

  it("should pass context parameters to segment event", () => {
    const service = new AnalyticsService();
    service.setContext({ context: 42 });
    service.track(Namespace.CONNECTION, Action.CREATE, { actionDescription: "Created new connection" });
    expect(window.analytics.track).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ actionDescription: "Created new connection", context: 42 })
    );
  });
});
