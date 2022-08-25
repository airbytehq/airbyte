import { render, mockConnection } from "utils/testutils";

import SettingsView from "./SettingsView";

let mockIsAdvancedMode = false;
const setMockIsAdvancedMode = (newSetting: boolean) => {
  mockIsAdvancedMode = newSetting;
};
jest.mock("hooks/services/useAdvancedModeSetting", () => ({
  useAdvancedModeSetting() {
    return [mockIsAdvancedMode, setMockIsAdvancedMode];
  },
}));

jest.mock("hooks/services/useConnectionHook", () => ({
  useDeleteConnection: () => ({ mutateAsync: () => null }),
  useGetConnectionState: () => ({ state: null, globalState: null, streamState: null }),
}));

// Mocking the DeleteBlock component is a bit ugly, but it's simpler and less
// brittle than mocking the providers it depends on; at least it's a direct,
// visible dependency of the component under test here.
//
// This mock is intentionally trivial; if anything to do with this component is
// to be tested, we'll have to bite the bullet and render it properly, within
// the necessary providers.
jest.mock("components/DeleteBlock", () => () => {
  const MockDeleteBlock = () => <div>Does not actually delete anything</div>;
  return <MockDeleteBlock />;
});

describe("<SettingsView />", () => {
  test("it only renders connection state when advanced mode is enabled", async () => {
    let container: HTMLElement;

    setMockIsAdvancedMode(false);
    ({ container } = await render(<SettingsView connection={mockConnection} />));
    expect(container.textContent).not.toContain("Connection State");

    setMockIsAdvancedMode(true);
    ({ container } = await render(<SettingsView connection={mockConnection} />));
    expect(container.textContent).toContain("Connection State");
  });
});
