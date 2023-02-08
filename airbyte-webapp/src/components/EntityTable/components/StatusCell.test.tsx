import { render, waitFor } from "@testing-library/react";
import { TestWrapper, TestSuspenseBoundary } from "test-utils";

import { StatusCell } from "./StatusCell";

jest.mock("hooks/services/useConnectionHook", () => ({
  useConnectionList: jest.fn(() => ({
    connections: [],
  })),
  useEnableConnection: jest.fn(() => ({
    mutateAsync: jest.fn(),
  })),
  useSyncConnection: jest.fn(() => ({
    mutateAsync: jest.fn(),
  })),
}));

const mockId = "mock-id";

jest.doMock("hooks/services/useConnectionHook", () => ({
  useEnableConnection: () => ({
    mutateAsync: jest.fn(),
    isLoading: false,
  }),
}));

describe("<StatusCell />", () => {
  it("renders switch when connection has schedule", () => {
    const { getByTestId } = render(
      <TestSuspenseBoundary>
        <StatusCell id={mockId} allowSync enabled />
      </TestSuspenseBoundary>,
      {
        wrapper: TestWrapper,
      }
    );

    const switchElement = getByTestId("enable-connection-switch");

    expect(switchElement).toBeEnabled();
    expect(switchElement).toBeChecked();
  });

  it("renders button when connection does not have schedule", async () => {
    const { getByTestId } = render(
      <TestSuspenseBoundary>
        <StatusCell id={mockId} allowSync enabled isManual />
      </TestSuspenseBoundary>,
      {
        wrapper: TestWrapper,
      }
    );

    await waitFor(() => expect(getByTestId("manual-sync-button")).toBeEnabled());
  });

  it("disables switch when hasBreakingChange is true", () => {
    const { getByTestId } = render(
      <TestSuspenseBoundary>
        <StatusCell id={mockId} allowSync hasBreakingChange />
      </TestSuspenseBoundary>,
      {
        wrapper: TestWrapper,
      }
    );

    expect(getByTestId("enable-connection-switch")).toBeDisabled();
  });

  it("disables manual sync button when hasBreakingChange is true", () => {
    const { getByTestId } = render(
      <TestSuspenseBoundary>
        <StatusCell id={mockId} allowSync hasBreakingChange enabled isManual />
      </TestSuspenseBoundary>,
      {
        wrapper: TestWrapper,
      }
    );

    expect(getByTestId("manual-sync-button")).toBeDisabled();
  });
});
