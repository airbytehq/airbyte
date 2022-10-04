import { Text } from "components/ui/Text";

import styles from "./CountDownTimer.module.scss";
import { useCountdown } from "./use-countdown";
export const CountDownTimer: React.FC<{ expiredOfferDate: string }> = ({ expiredOfferDate }) => {
  const [hours, minutes, seconds] = useCountdown(expiredOfferDate);

  return (
    <div className={styles.flex}>
      <Text as="h2" className={styles.textColorOrange}>
        {hours.toString().padStart(2, "0")}h
      </Text>
      <Text as="h2" className={styles.textColorOrange}>
        {minutes.toString().padStart(2, "0")}m{" "}
      </Text>
      <Text as="h2" className={styles.textColorOrange}>
        {seconds.toString().padStart(2, "0")}s
      </Text>
    </div>
  );
};
