import { fireEvent, render } from "@testing-library/react";
import React from "react";
import { TestWrapper } from "test-utils/testutils";

import { Experiments } from "hooks/services/Experiment/experiments";
import * as ExperimentService from "hooks/services/Experiment/ExperimentService";
import { RoutePaths } from "pages/routePaths";

import { CloudSettingsRoutes } from "../../settings/routePaths";

const mockToggleInviteUsersModalOpen = jest.fn();
jest.doMock("packages/cloud/services/users/InviteUsersModalService", () => ({
  InviteUsersModalServiceProvider: ({ children }: { children: React.ReactNode }): JSX.Element => <>{children}</>,
  useInviteUsersModalService: () => ({
    toggleInviteUsersModalOpen: mockToggleInviteUsersModalOpen,
  }),
}));

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { InviteUsersHint } = require("./InviteUsersHint");

const createUseExperimentMock =
  (options: { visible?: boolean; linkToUsersPage?: boolean }) => (key: keyof Experiments) => {
    switch (key) {
      case "connector.inviteUsersHint.visible":
        return options.visible ?? false;
      case "connector.inviteUsersHint.linkToUsersPage":
        return options.linkToUsersPage ?? false;
      default:
        throw new Error(`${key} is not mocked`);
    }
  };

describe("InviteUsersHint", () => {
  beforeEach(() => {
    mockToggleInviteUsersModalOpen.mockReset();
  });

  it("does not render by default", () => {
    const { queryByTestId } = render(<InviteUsersHint connectorType="source" />, { wrapper: TestWrapper });
    expect(queryByTestId("inviteUsersHint")).not.toBeInTheDocument();
  });

  it("renders when `connector.inviteUserHint.visible` is set to `true`", () => {
    jest.spyOn(ExperimentService, "useExperiment").mockImplementation(createUseExperimentMock({ visible: true }));

    const { getByTestId } = render(<InviteUsersHint connectorType="source" />, { wrapper: TestWrapper });
    const element = getByTestId("inviteUsersHint");
    expect(element).toBeInTheDocument();
  });

  it("opens modal when clicking on CTA by default", () => {
    jest.spyOn(ExperimentService, "useExperiment").mockImplementation(createUseExperimentMock({ visible: true }));

    const { getByTestId } = render(<InviteUsersHint connectorType="source" />, { wrapper: TestWrapper });
    const element = getByTestId("inviteUsersHint-cta");

    expect(element).not.toHaveAttribute("href");

    fireEvent.click(element);
    expect(mockToggleInviteUsersModalOpen).toHaveBeenCalledTimes(1);
  });

  it("opens link to access-management settings when clicking on CTA and `connector.inviteUsersHint.linkToUsersPage` is `true`", () => {
    jest
      .spyOn(ExperimentService, "useExperiment")
      .mockImplementation(createUseExperimentMock({ visible: true, linkToUsersPage: true }));

    const { getByTestId } = render(<InviteUsersHint connectorType="source" />, { wrapper: TestWrapper });
    const element = getByTestId("inviteUsersHint-cta");

    expect(element).toHaveAttribute("href", `../${RoutePaths.Settings}/${CloudSettingsRoutes.AccessManagement}`);

    fireEvent.click(element);
    expect(mockToggleInviteUsersModalOpen).not.toHaveBeenCalled();
  });
});
