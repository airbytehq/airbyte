import { Text } from "components/base/Text";

import styles from "./CountDownTimer.module.scss";
import { useCountdown } from "./use-countdown";
export const CountDownTimer: React.FC<{ expiredOfferDate: string }> = ({ expiredOfferDate }) => {
  const [hours, minutes, seconds] = useCountdown(expiredOfferDate);

  return (
    <div className={styles.flex}>
      {" "}
      <div className={styles.countdownItem}>
        <Text bold>{hours.toString().padStart(2, "0")}</Text> <Text>hours </Text>
      </div>
      <div className={styles.countdownItem}>
        <Text bold>{minutes.toString().padStart(2, "0")} </Text>
        <Text> minutes </Text>
      </div>
      <div className={styles.countdownItem}>
        <Text bold>{seconds.toString().padStart(2, "0")} </Text> <Text>seconds </Text>
      </div>
    </div>
  );
};
