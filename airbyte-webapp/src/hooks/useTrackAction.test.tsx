import { renderHook } from "@testing-library/react-hooks";

import { useAnalyticsService } from "./services/Analytics/useAnalyticsService";
import { TrackActionLegacyType, TrackActionNamespace, TrackActionType, useTrackAction } from "./useTrackAction";

jest.mock("./services/Analytics/useAnalyticsService", () => {
  const mockTrack = jest.fn();
  return { useAnalyticsService: () => ({ track: mockTrack }) };
});

describe("With legacy namespace", () => {
  test("it parses namespace and legacy name when calling the hook", () => {
    const mockUseTrackAction = renderHook(() =>
      useTrackAction(TrackActionNamespace.SOURCE, TrackActionLegacyType.NEW_SOURCE)
    );
    mockUseTrackAction.result.current("test action sent", TrackActionType.CREATE, {});
    const analyticsService = useAnalyticsService();

    expect(analyticsService.track).toHaveBeenCalledWith(
      "Airbyte.UI.Source.Create",
      expect.objectContaining({ legacy_event_name: "New Source - Action" })
    );
  });
});

describe("Without legacy namespace", () => {
  test("legacy namespace is passed as empty string if none is received", () => {
    const mockUseTrackAction = renderHook(() => useTrackAction(TrackActionNamespace.CONNECTION));
    mockUseTrackAction.result.current("another test action", TrackActionType.CREATE, {});
    const analyticsService = useAnalyticsService();
    expect(analyticsService.track).toHaveBeenCalledWith(
      "Airbyte.UI.Connection.Create",
      expect.objectContaining({ legacy_event_name: "" })
    );
  });
});
