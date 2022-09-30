import classnames from "classnames";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { CountDownTimer } from "components/experiments/SpeedyConnection/CountDownTimer";
import { Button } from "components/ui";
import { Text } from "components/ui/Text";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";
import { StepType } from "pages/OnboardingPage/types";
import { RoutePaths } from "pages/routePaths";

import { useExperimentSpeedyConnection } from "../hooks/use-experiment-speedy-connection-experiment";
import styles from "./SpeedyConnectionBanner.module.scss";
export const SpeedyConnectionBanner = () => {
  const { expiredOfferDate } = useExperimentSpeedyConnection();
  const analyticsService = useAnalyticsService();
  const navigate = useNavigate();
  const handleClick = () => {
    // Send track event with experiment info
    analyticsService.track(Namespace.ONBOARDING, Action.START, {
      actionDescription: "Start Onboarding",
      posthog_experiment: "exp-speedy-connection",
    });
    navigate(RoutePaths.Onboarding, {
      state: {
        step: StepType.CREATE_SOURCE,
      },
    });
  };
  return (
    <div className={classnames(styles.container)}>
      <div className={classnames(styles.innerContainer)}>
        <div className={classnames(styles.firstColumn)}>
          <Text> Set up your first connection in the next</Text>
          <CountDownTimer {...{ expiredOfferDate }} />
          <Text>
            {" "}
            and get <strong>100 </strong> additonal credits for your trial
          </Text>
        </div>
        <div className={classnames(styles.secondColumn)}>
          <Button onClick={handleClick}>
            <FormattedMessage id="onboarding.firstConnection" />
          </Button>
        </div>
      </div>
    </div>
  );
};
