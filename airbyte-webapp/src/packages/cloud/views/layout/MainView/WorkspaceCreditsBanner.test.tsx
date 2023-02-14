import { render } from "@testing-library/react";
import { Suspense } from "react";
import { TestWrapper } from "test-utils";

import { I18nProvider } from "core/i18n";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";

import { WorkspaceStatusBanner } from "./WorkspaceStatusBanner";
import cloudLocales from "../../../locales/en.json";

jest.mock("services/workspaces/WorkspacesService", () => ({
  useCurrentWorkspace: () => ({
    workspace: { workspaceId: "123" },
  }),
}));

jest.mock("packages/cloud/services/workspaces/CloudWorkspacesService");
const mockUseGetCloudWorkspace = useGetCloudWorkspace as unknown as jest.Mock<Partial<typeof useGetCloudWorkspace>>;

const setHasWorkspaceBanner = jest.fn();

const workspaceStatusBannerWithWrapper = (
  <TestWrapper>
    <Suspense fallback="this should not render">
      <I18nProvider messages={cloudLocales} locale="en">
        <WorkspaceStatusBanner setHasWorkspaceCreditsBanner={setHasWorkspaceBanner} />
      </I18nProvider>
    </Suspense>
  </TestWrapper>
);

describe("WorkspaceCreditsBanner", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should render credits problem banner for credits problem pre-trial", () => {
    mockUseGetCloudWorkspace.mockImplementationOnce(() => {
      return { workspaceTrialStatus: "pre_trial", creditStatus: CreditStatus.NEGATIVE_BEYOND_GRACE_PERIOD };
    });

    const { getByText } = render(workspaceStatusBannerWithWrapper);
    expect(getByText(/You’re out of credits!/)).toBeTruthy();
    expect(setHasWorkspaceBanner).toHaveBeenCalledWith(true);
  });
  it("should render credits problem banner for credits problem during trial", () => {
    mockUseGetCloudWorkspace.mockImplementationOnce(() => {
      return { workspaceTrialStatus: "in_trial", creditStatus: CreditStatus.NEGATIVE_BEYOND_GRACE_PERIOD };
    });

    const { getByText } = render(workspaceStatusBannerWithWrapper);
    expect(getByText(/You’re out of credits!/)).toBeTruthy();
    expect(setHasWorkspaceBanner).toHaveBeenCalledWith(true);
  });

  it("should render credits problem banner for credits problem after trial", () => {
    mockUseGetCloudWorkspace.mockImplementationOnce(() => {
      return { workspaceTrialStatus: "out_of_trial", creditStatus: CreditStatus.NEGATIVE_BEYOND_GRACE_PERIOD };
    });

    const { getByText } = render(workspaceStatusBannerWithWrapper);
    expect(getByText(/You’re out of credits!/)).toBeTruthy();
    expect(setHasWorkspaceBanner).toHaveBeenCalledWith(true);
  });

  it("should render pre-trial banner if user's trial has not started", () => {
    mockUseGetCloudWorkspace.mockImplementationOnce(() => {
      return { creditStatus: CreditStatus.POSITIVE, workspaceTrialStatus: "pre_trial", trialExpiryTimestamp: null };
    });

    const { getByText } = render(workspaceStatusBannerWithWrapper);
    expect(getByText(/Your 14-day trial of Airbyte will start/)).toBeTruthy();
    expect(setHasWorkspaceBanner).toHaveBeenCalledWith(true);
  });

  it("should render trial banner if user is in trial", () => {
    // create a date that is 1 day in the future
    const trialExpiryDate = new Date();
    trialExpiryDate.setDate(trialExpiryDate.getDate() + 1);

    mockUseGetCloudWorkspace.mockImplementationOnce(() => {
      return {
        creditStatus: CreditStatus.POSITIVE,
        workspaceTrialStatus: "in_trial",
        // use getTime() to get the number of milliseconds since epoch
        trialExpiryTimestamp: trialExpiryDate.getTime(),
      };
    });

    const { getByText } = render(workspaceStatusBannerWithWrapper);
    expect(getByText(/You are using a trial of Airbyte/)).toBeTruthy();
    expect(getByText(/1 day/)).toBeTruthy();
    expect(setHasWorkspaceBanner).toHaveBeenCalledWith(true);
  });
  it("should render an empty banner if user is in trial", () => {
    mockUseGetCloudWorkspace.mockImplementationOnce(() => {
      return {
        creditStatus: CreditStatus.POSITIVE,
        workspaceTrialStatus: "out_of_trial",
      };
    });

    const { container } = render(workspaceStatusBannerWithWrapper);
    expect(container).toBeEmptyDOMElement();
    expect(setHasWorkspaceBanner).toHaveBeenCalledWith(false);
  });
});
