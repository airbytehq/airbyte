import { useRef, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useUnmount } from "react-use";
import { Subscription } from "rxjs";

import { Spinner } from "components";

import { useExperiment } from "hooks/services/Experiment";
import { OAuthProviders } from "packages/cloud/lib/auth/AuthProviders";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import githubLogo from "./assets/github-logo.svg";
import googleLogo from "./assets/google-logo.svg";
import styles from "./OAuthLogin.module.scss";

const GitHubButton: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  return (
    <button className={styles.github} onClick={onClick} data-testid="githubOauthLogin">
      <img src={githubLogo} alt="" />
      <FormattedMessage id="login.oauth.github" tagName="span" />
    </button>
  );
};

const GoogleButton: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  return (
    <button className={styles.google} onClick={onClick} data-testid="googleOauthLogin">
      <img src={googleLogo} alt="" />
      <FormattedMessage id="login.oauth.google" tagName="span" />
    </button>
  );
};

interface OAuthLoginProps {
  isSignUpPage?: boolean;
}

export const OAuthLogin: React.FC<OAuthLoginProps> = ({ isSignUpPage }) => {
  const { formatMessage } = useIntl();
  const { loginWithOAuth } = useAuthService();
  const stateSubscription = useRef<Subscription>();
  const [errorCode, setErrorCode] = useState<string>();
  const [isLoading, setLoading] = useState(false);

  const isGitHubLoginEnabled = useExperiment("authPage.oauth.github", true);
  const isGoogleLoginEnabled = useExperiment("authPage.oauth.google", true);
  const isGitHubEnabledOnSignUp = useExperiment("authPage.oauth.github.signUpPage", true);
  const isGoogleEnabledOnSignUp = useExperiment("authPage.oauth.google.signUpPage", true);

  const showGoogleLogin = isGoogleLoginEnabled && (!isSignUpPage || isGoogleEnabledOnSignUp);
  const showGitHubLogin = isGitHubLoginEnabled && (!isSignUpPage || isGitHubEnabledOnSignUp);

  const isAnyOauthEnabled = showGoogleLogin || showGitHubLogin;

  useUnmount(() => {
    stateSubscription.current?.unsubscribe();
  });

  if (!isAnyOauthEnabled) {
    return null;
  }

  const getErrorMessage = (error: string): string | undefined => {
    switch (error) {
      // The following error codes are not really errors, thus we'll ignore them.
      case "auth/popup-closed-by-user":
      case "auth/user-cancelled":
      case "auth/cancelled-popup-request":
        return undefined;
      case "auth/account-exists-with-different-credential":
        // Happens if a user requests and sets a password for an originally OAuth account.
        // From them on they can't login via OAuth anymore unless it's Google OAuth.
        return formatMessage({ id: "login.oauth.differentCredentialsError" });
      default:
        return formatMessage({ id: "login.oauth.unknownError" }, { error });
    }
  };

  const login = (provider: OAuthProviders) => {
    setErrorCode(undefined);
    stateSubscription.current?.unsubscribe();
    stateSubscription.current = loginWithOAuth(provider).subscribe({
      next: (value) => {
        if (value === "loading") {
          setLoading(true);
        }
        if (value === "done") {
          setLoading(false);
        }
      },
      error: (error) => {
        if ("code" in error && typeof error.code === "string") {
          setErrorCode(error.code);
        }
      },
    });
  };

  const errorMessage = errorCode ? getErrorMessage(errorCode) : undefined;

  return (
    <div>
      <div className={styles.separator}>
        <FormattedMessage id="login.oauth.or" />
      </div>
      {isLoading && (
        <div className={styles.spinner}>
          <Spinner />
        </div>
      )}
      {!isLoading && (
        <div className={styles.buttons}>
          {showGoogleLogin && <GoogleButton onClick={() => login("google")} />}
          {showGitHubLogin && <GitHubButton onClick={() => login("github")} />}
        </div>
      )}
      {errorMessage && <div className={styles.error}>{errorMessage}</div>}
    </div>
  );
};
