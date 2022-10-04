import classnames from "classnames";
import classNames from "classnames";
import { FormattedMessage } from "react-intl";
import { Link, useLocation } from "react-router-dom";

import { CountDownTimer } from "components/experiments/SpeedyConnection/CountDownTimer";
import { Text } from "components/ui/Text";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";
import { StepType } from "pages/OnboardingPage/types";
import { RoutePaths } from "pages/routePaths";

import { useExperimentSpeedyConnection } from "../hooks/use-experiment-speedy-connection-experiment";
import credits from "./credits.svg";
import styles from "./SpeedyConnectionBanner.module.scss";

export const SpeedyConnectionBanner = () => {
  const { expiredOfferDate } = useExperimentSpeedyConnection();
  const analyticsService = useAnalyticsService();
  const location = useLocation();

  return (
    <div className={classnames(styles.container)}>
      <div className={styles.innerContainer}>
        <img src={credits} alt="" />

        <Link
          className={classNames(styles.linkCta, {
            [styles.textDecorationNone]: location.pathname.includes("onboarding"),
          })}
          to={RoutePaths.Onboarding}
          state={{
            step: StepType.CREATE_SOURCE,
          }}
          onClick={() =>
            analyticsService.track(Namespace.ONBOARDING, Action.START_EXP_SPEEDY_CONNECTION, {
              actionDescription: "Start Onboarding speedy connection experiment",
            })
          }
        >
          <Text>
            <FormattedMessage
              id="experiment.speedyConnection.firstConnection"
              defaultMessage="Set up your first connection "
            />{" "}
          </Text>
        </Link>
        <Text>
          <FormattedMessage id="experiment.speedyConnection.next" defaultMessage="in the next" />{" "}
        </Text>

        <CountDownTimer {...{ expiredOfferDate }} />
        <Text>
          <FormattedMessage
            id="experiment.speedyConnection.offer"
            defaultMessage=" and get <b>100 additonal credits </b>for your trial"
          />
        </Text>
        <img src={credits} alt="" />
      </div>
    </div>
  );
};
