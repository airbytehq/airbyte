import classnames from "classnames";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";

import { Text } from "components/ui/Text";

import { CountDownTimer } from "packages/cloud/components/experiments/SpeedyConnection/CountDownTimer";
import { RoutePaths } from "pages/routePaths";

import { useExperimentSpeedyConnection } from "../hooks/useExperimentSpeedyConnection";
import styles from "./SpeedyConnectionBanner.module.scss";

export const SpeedyConnectionBanner = () => {
  const { expiredOfferDate } = useExperimentSpeedyConnection();

  return (
    <div className={classnames(styles.container)}>
      <div className={styles.innerContainer}>
        <FormattedMessage
          id="experiment.speedyConnection"
          defaultMessage="<link>Set up your first connection</link> in the next <timer></timer> and get <b>100 additonal credits</b> for your trial"
          values={{
            link: (link: React.ReactNode[]) => (
              <Link className={styles.linkCta} to={`${RoutePaths.Connections}/${RoutePaths.ConnectionNew}`}>
                <Text bold>{link}</Text>
              </Link>
            ),
            timer: () => <CountDownTimer expiredOfferDate={expiredOfferDate} />,
          }}
        />
      </div>
    </div>
  );
};
