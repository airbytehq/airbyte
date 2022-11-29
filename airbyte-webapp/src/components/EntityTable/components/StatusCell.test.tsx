import { render } from "@testing-library/react";
import { TestWrapper } from "test-utils/testutils";

import StatusCell from "./StatusCell";

const mockId = "mock-id";

jest.doMock("hooks/services/useConnectionHook", () => ({
  useEnableConnection: () => ({
    mutateAsync: jest.fn(),
    isLoading: false,
  }),
}));

describe("<StatusCell />", () => {
  it("renders switch when connection is not manual", () => {
    const { getByTestId } = render(<StatusCell id={mockId} onSync={jest.fn()} allowSync enabled />, {
      wrapper: TestWrapper,
    });

    const switchElement = getByTestId("enable-connection-switch");

    expect(switchElement).toBeEnabled();
    expect(switchElement).toBeChecked();
  });

  it("disables switch when hasBreakingChange is true", () => {
    const { getByTestId } = render(<StatusCell id={mockId} onSync={jest.fn()} allowSync hasBreakingChange />, {
      wrapper: TestWrapper,
    });

    expect(getByTestId("enable-connection-switch")).toBeDisabled();
  });
});
