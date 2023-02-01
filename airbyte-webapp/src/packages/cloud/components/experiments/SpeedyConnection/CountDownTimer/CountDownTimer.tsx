import { Text } from "components/ui/Text";

import styles from "./CountDownTimer.module.scss";
import { useCountdown } from "./useCountdown";
export const CountDownTimer: React.FC<{ expiredOfferDate: string }> = ({ expiredOfferDate }) => {
  const [hours, minutes] = useCountdown(expiredOfferDate);

  return (
    <div className={styles.countDownTimerContainer}>
      <Text className={styles.countDownTimerItem}>{hours.toString().padStart(2, "0")}h</Text>
      <Text className={styles.countDownTimerItem}>{minutes.toString().padStart(2, "0")}m</Text>
    </div>
  );
};
