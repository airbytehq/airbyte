import { render } from "@testing-library/react";
import userEvents from "@testing-library/user-event";
import { EMPTY } from "rxjs";

import type { useExperiment } from "hooks/services/Experiment";
import type { Experiments } from "hooks/services/Experiment/experiments";
import { TestWrapper } from "utils/testutils";

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

const createUseExperimentMock = (options: {
  google?: boolean;
  github?: boolean;
  googleSignUp?: boolean;
  githubSignUp?: boolean;
}) => {
  return (key: keyof Experiments) => {
    switch (key) {
      case "authPage.oauth.github":
        return options.github ?? false;
      case "authPage.oauth.google":
        return options.google ?? false;
      case "authPage.oauth.github.signUpPage":
        return options.githubSignUp ?? true;
      case "authPage.oauth.google.signUpPage":
        return options.googleSignUp ?? true;
      default:
        throw new Error(`${key} is not mocked`);
    }
  };
};

describe("OAuthLogin", () => {
  beforeEach(() => {
    mockUseExperiment.mockReset();
    mockUseExperiment.mockReturnValue(true);
    mockLoginWithOAuth.mockReset();
    mockLoginWithOAuth.mockReturnValue(EMPTY);
  });

  it("should render all enabled logins", () => {
    mockUseExperiment.mockImplementation(createUseExperimentMock({ google: true, github: true }));
    const { getByTestId } = render(<OAuthLogin />, { wrapper: TestWrapper });
    expect(getByTestId("googleOauthLogin")).toBeInTheDocument();
    expect(getByTestId("githubOauthLogin")).toBeInTheDocument();
  });

  it("should not render buttons that are disabled", () => {
    mockUseExperiment.mockImplementation(createUseExperimentMock({ google: false, github: true }));
    const { getByTestId, queryByTestId } = render(<OAuthLogin />, { wrapper: TestWrapper });
    expect(queryByTestId("googleOauthLogin")).not.toBeInTheDocument();
    expect(getByTestId("githubOauthLogin")).toBeInTheDocument();
  });

  it("should not render disabled buttons for sign-up page", () => {
    mockUseExperiment.mockImplementation(createUseExperimentMock({ google: true, github: true, googleSignUp: false }));
    const { getByTestId, queryByTestId } = render(<OAuthLogin isSignUpPage />, { wrapper: TestWrapper });
    expect(queryByTestId("googleOauthLogin")).not.toBeInTheDocument();
    expect(getByTestId("githubOauthLogin")).toBeInTheDocument();
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
