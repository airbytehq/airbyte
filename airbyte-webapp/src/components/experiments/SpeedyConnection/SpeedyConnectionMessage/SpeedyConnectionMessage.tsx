import { FormattedMessage } from "react-intl";

import { CountDownTimer } from "components/experiments/SpeedyConnection/CountDownTimer";
import { Button } from "components/ui";
import { Text } from "components/ui/Text";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

import { useExperimentSpeedyConnection } from "../hooks/use-experiment-speedy-connection-experiment";
import styles from "./SpeedyConnectionMessage.module.scss";

export const SpeedyConnectionMessage = ({ onClick }: { onClick: () => void }) => {
  const analyticsService = useAnalyticsService();
  const { expiredOfferDate } = useExperimentSpeedyConnection();
  const handleClick = () => {
    analyticsService.track(Namespace.ONBOARDING, Action.START, {
      actionDescription: "Start Onboarding",
      posthog_experiment: "exp-speedy-connection",
    });
    onClick();
  };
  return (
    <>
      <div className={styles.message}>
        <Text> Set up your first connection in the next</Text>
        <CountDownTimer {...{ expiredOfferDate }} />
        <Text>
          {" "}
          and get <strong>100 </strong> additonal credits for your trial
        </Text>
      </div>

      <Button size="lg" onClick={handleClick}>
        <FormattedMessage id="onboarding.firstConnection" />
      </Button>
    </>
  );
};
