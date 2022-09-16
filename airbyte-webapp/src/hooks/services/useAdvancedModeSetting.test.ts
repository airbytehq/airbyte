import { act, renderHook } from "@testing-library/react-hooks";

import { useAdvancedModeSetting } from "./useAdvancedModeSetting";

// mock `useCurrentWorkspace` with a closure so we can simulate changing
// workspaces by mutating the top-level variable it references
let mockWorkspaceId = "fakeWorkspaceId";
const changeToWorkspace = (newWorkspaceId: string) => {
  mockWorkspaceId = newWorkspaceId;
};

jest.mock("hooks/services/useWorkspace", () => ({
  useCurrentWorkspace() {
    return { workspaceId: mockWorkspaceId };
  },
}));

it("defaults to false before advanced mode is explicitly set", () => {
  const { result } = renderHook(() => useAdvancedModeSetting());
  // eslint-disable-next-line prefer-const
  let [isAdvancedMode, setAdvancedMode] = result.current;

  expect(isAdvancedMode).toBe(false);

  act(() => setAdvancedMode(true));
  [isAdvancedMode] = result.current;

  expect(isAdvancedMode).toBe(true);
});

it("stores workspace-specific advanced mode settings", () => {
  changeToWorkspace("workspaceA");

  const { result, rerender } = renderHook(() => useAdvancedModeSetting());
  // Avoiding destructuring in this spec to avoid capturing stale values when
  // rerendering in different workspaces
  const setAdvancedModeA = result.current[1];

  expect(result.current[0]).toBe(false);
  act(() => setAdvancedModeA(true));

  expect(result.current[0]).toBe(true);

  // in workspaceB, it returns the default setting of `false`
  changeToWorkspace("workspaceB");
  rerender();
  expect(result.current[0]).toBe(false);

  // ...but workspaceA's manual setting is persisted
  changeToWorkspace("workspaceA");
  rerender();
  expect(result.current[0]).toBe(true);
});
