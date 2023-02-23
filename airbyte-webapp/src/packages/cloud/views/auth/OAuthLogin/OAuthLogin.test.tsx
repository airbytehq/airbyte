import { render } from "@testing-library/react";
import userEvents from "@testing-library/user-event";
import { EMPTY } from "rxjs";
import { TestWrapper } from "test-utils/testutils";

import type { useExperiment } from "hooks/services/Experiment";

const mockUseExperiment = jest.fn<ReturnType<typeof useExperiment>, Parameters<typeof useExperiment>>();
jest.doMock("hooks/services/Experiment", () => ({
  useExperiment: mockUseExperiment,
}));

const mockLoginWithOAuth = jest.fn();
jest.doMock("packages/cloud/services/auth/AuthService", () => ({
  useAuthService: () => ({
    loginWithOAuth: mockLoginWithOAuth,
  }),
}));

// We need to use require here, so that this really happens after the doMock calls above
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { OAuthLogin } = require("./OAuthLogin");

describe("OAuthLogin", () => {
  beforeEach(() => {
    mockUseExperiment.mockReset();
    mockUseExperiment.mockReturnValue(true);
    mockLoginWithOAuth.mockReset();
    mockLoginWithOAuth.mockReturnValue(EMPTY);
  });

  it("should call auth service for Google", () => {
    const { getByTestId } = render(<OAuthLogin />, { wrapper: TestWrapper });
    userEvents.click(getByTestId("googleOauthLogin"));
    expect(mockLoginWithOAuth).toHaveBeenCalledWith("google");
  });

  it("should call auth service for GitHub", () => {
    const { getByTestId } = render(<OAuthLogin />, { wrapper: TestWrapper });
    userEvents.click(getByTestId("githubOauthLogin"));
    expect(mockLoginWithOAuth).toHaveBeenCalledWith("github");
  });
});
