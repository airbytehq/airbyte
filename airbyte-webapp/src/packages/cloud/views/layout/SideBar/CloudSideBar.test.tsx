import { render, screen } from "@testing-library/react";
import { Suspense } from "react";
import { TestWrapper } from "test-utils/testutils";

import { CloudSideBar } from "./CloudSideBar";

jest.mock("hooks/services/useWorkspace", () => ({
  useCurrentWorkspace: () => {
    return { workspaceId: "123" };
  },
}));
jest.mock("packages/cloud/services/workspaces/CloudWorkspacesService", () => ({
  useGetCloudWorkspace: () => {
    return {
      remainingCredits: 100,
    };
  },
}));

jest.mock("packages/cloud/services/thirdParty/intercom", () => ({
  useIntercom: () => {
    return { show: jest.fn() };
  },
}));

jest.mock("../../workspaces/WorkspacePopout", () => ({
  WorkspacePopout: ({ children }: { children: (props: { onOpen: () => void; value: string }) => JSX.Element }) => {
    return children({ onOpen: jest.fn(), value: "test" });
  },
}));

describe("<SideBar/>", () => {
  it("renders the main nav items", () => {
    render(
      <TestWrapper>
        <Suspense fallback="loading">
          <CloudSideBar />
        </Suspense>
      </TestWrapper>
    );
    const navItems = screen.getByTestId("navMainItems").querySelectorAll("li");
    expect(navItems.length).toBe(3);

    screen.getByTestId("connectionsLink");
    screen.getByTestId("sourcesLink");
    screen.getByTestId("destinationsLink");
  });
  it("renders cloud-specific items passed in", () => {
    render(
      <TestWrapper>
        <Suspense fallback="loading">
          <CloudSideBar />
        </Suspense>
      </TestWrapper>
    );

    const workspaceButton = screen.getByTestId("workspaceButton");
    expect(workspaceButton).toBeInTheDocument();

    const listItems = screen.getByTestId("navBottomMenu").querySelectorAll("li");
    expect(listItems.length).toBe(4);
    expect(listItems[0]).toContainHTML('data-testid="creditsButton"');
    expect(listItems[3]).not.toContainHTML("dev"); // version info should not be present on cloud
  });
});
