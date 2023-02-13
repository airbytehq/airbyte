import { render } from "@testing-library/react";
import { Suspense } from "react";
import { TestWrapper } from "test-utils";

import { I18nProvider } from "core/i18n";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";

import { WorkspaceCreditsBanner } from "./WorkspaceCreditsBanner";
import cloudLocales from "../../../locales/en.json";

jest.mock("services/workspaces/WorkspacesService", () => ({
  useCurrentWorkspace: () => ({
    workspace: { workspaceId: "123" },
  }),
}));

jest.mock("packages/cloud/services/workspaces/CloudWorkspacesService");
const mockUseGetCloudWorkspace = useGetCloudWorkspace as unknown as jest.Mock<Partial<typeof useGetCloudWorkspace>>;
const baseUseGetCloudWorkspace = {
  cloudWorkspace: {
    workspaceTrialStatus: "pre_trial",
    trialExpiryTimestamp: null,
    creditStatus: CreditStatus.POSITIVE,
  },
};

describe("WorkspaceCreditsBanner", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render pre-trial if user's trial has not started", () => {
    mockUseGetCloudWorkspace.mockImplementationOnce(() => {
      const { cloudWorkspace } = baseUseGetCloudWorkspace;

      return cloudWorkspace;
    });
    const { getByText } = render(
      <TestWrapper>
        <Suspense fallback="this should not render">
          <I18nProvider messages={cloudLocales} locale="en">
            <WorkspaceCreditsBanner setHasWorkspaceCreditsBanner={jest.fn} />
          </I18nProvider>
        </Suspense>
      </TestWrapper>
    );
    expect(getByText("Your 14-day trial of Airbyte will start once your first sync has completed.")).toBeTruthy();
  });
});

/**
 * test cases:
 * - test hierarchy of logic
 *   - credit balance > trial > pre-trial > null
 *     - test return string
 *     - test that `setHasWorkspaceCreditsBanner` is called as expected
 */

// eslint-disable-next-line jest/no-export
export {};
