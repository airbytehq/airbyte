import { faCaretDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { Text } from "../Text";
import styles from "./PillButton.module.scss";

export type PillButtonVariant = "grey" | "blue" | "green" | "red" | "strong-red" | "strong-blue";

const STYLES_BY_VARIANT: Readonly<Record<PillButtonVariant, string>> = {
  grey: styles.grey,
  blue: styles.blue,
  green: styles.green,
  red: styles.red,
  "strong-red": styles.strongRed,
  "strong-blue": styles.strongBlue,
};

interface PillButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
  variant?: PillButtonVariant;
  labels?: React.ReactNode[];
}

export const PillButton: React.FC<PillButtonProps> = ({ active, variant = "grey", labels = [], ...buttonProps }) => {
  const buttonClassName = classNames(
    styles.button,
    {
      [styles.active]: active,
      [styles.disabled]: buttonProps.disabled,
    },
    STYLES_BY_VARIANT[variant],
    buttonProps.className
  );
  return (
    <button type="button" {...buttonProps} className={buttonClassName}>
      {labels.map((label, index) => (
        <>
          <div className={styles.labelContainer}>
            <Text as="span" size="xs" className={styles.text}>
              {label}
            </Text>
          </div>
          {index !== labels?.length - 1 && <div className={styles.divider} />}
        </>
      ))}
      <FontAwesomeIcon className={styles.icon} icon={faCaretDown} />
    </button>
  );
};
