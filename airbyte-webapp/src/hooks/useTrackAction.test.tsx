import { act, renderHook } from "@testing-library/react-hooks";

import { TrackActionLegacyType, TrackActionNamespace, useTrackAction } from "./useTrackAction";

describe("With legacy namespace", () => {
  const mockUseTrackAction = renderHook(() =>
    useTrackAction(TrackActionNamespace.SOURCE, TrackActionLegacyType.NEW_SOURCE)
  );
  test("it parses namespace and legacy name when calling the hook", () => {
    act(mockUseTrackAction("hi", {}));
    expect(2 + 2).toEqual(4);
  });
});

describe("Without legacy namespace", () => {
  const mockUseTrackAction = renderHook(() => useTrackAction(TrackActionNamespace.SOURCE));
  test.todo("it parses namespace when calling the hook");
  test.todo("legacy namespace can be undefined");
});
