import { useRef, useState } from "react";
import { useUnmount } from "react-use";
import { Subscription } from "rxjs";

import { Spinner } from "components";

import { useExperiment } from "hooks/services/Experiment";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import png from "./assets/btn_google_signin_light_normal_web@2x.png";
import styles from "./OAuthLogin.module.scss";

export const OAuthLogin: React.FC = () => {
  const { loginWithOAuth } = useAuthService();
  const stateSubscription = useRef<Subscription>();
  const [isLoading, setLoading] = useState(false);

  const isGitHubLoginEnabled = useExperiment("authPage.oauth.github", false);
  const isGoogleLoginEnabled = useExperiment("authPage.oauth.google", false);

  const isAnyOauthEnabled = isGitHubLoginEnabled || isGoogleLoginEnabled;

  useUnmount(() => {
    stateSubscription.current?.unsubscribe();
  });

  const login = (provider: "google" | "github") => {
    const state = loginWithOAuth(provider);
    stateSubscription.current = state.subscribe((value) => {
      if (value === "loading") {
        setLoading(true);
      }
      if (value === "done") {
        setLoading(false);
      }
    });
  };

  if (!isAnyOauthEnabled) {
    return null;
  }

  return (
    <div className={styles.oauthLogin}>
      <div className={styles.separator}>or</div>
      {isLoading && <Spinner />}
      {!isLoading && isGoogleLoginEnabled && (
        <button onClick={() => login("google")} style={{ background: "none", border: "none" }}>
          <img src={png} />
        </button>
      )}
      {!isLoading && isGitHubLoginEnabled && (
        <button onClick={() => login("github")}>Login with your GitHub account</button>
      )}
    </div>
  );
};
