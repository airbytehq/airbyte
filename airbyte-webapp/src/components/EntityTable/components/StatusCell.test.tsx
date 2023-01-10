import { render } from "@testing-library/react";
import { TestWrapper } from "test-utils/testutils";

import { StatusCell } from "./StatusCell";

const mockId = "mock-id";

jest.doMock("hooks/services/useConnectionHook", () => ({
  useEnableConnection: () => ({
    mutateAsync: jest.fn(),
    isLoading: false,
  }),
}));

describe("<StatusCell />", () => {
  it("renders switch when connection has schedule", () => {
    const { getByTestId } = render(<StatusCell id={mockId} onSync={jest.fn()} allowSync enabled />, {
      wrapper: TestWrapper,
    });

    const switchElement = getByTestId("enable-connection-switch");

    expect(switchElement).toBeEnabled();
    expect(switchElement).toBeChecked();
  });

  it("renders button when connection does not have schedule", () => {
    const { getByTestId } = render(<StatusCell id={mockId} onSync={jest.fn()} allowSync enabled isManual />, {
      wrapper: TestWrapper,
    });

    expect(getByTestId("manual-sync-button")).toBeEnabled();
  });

  it("disables switch when hasBreakingChange is true", () => {
    const { getByTestId } = render(<StatusCell id={mockId} onSync={jest.fn()} allowSync hasBreakingChange />, {
      wrapper: TestWrapper,
    });

    expect(getByTestId("enable-connection-switch")).toBeDisabled();
  });

  it("disables manual sync button when hasBreakingChange is true", () => {
    const { getByTestId } = render(
      <StatusCell id={mockId} onSync={jest.fn()} allowSync hasBreakingChange enabled isManual />,
      {
        wrapper: TestWrapper,
      }
    );

    expect(getByTestId("manual-sync-button")).toBeDisabled();
  });
});
