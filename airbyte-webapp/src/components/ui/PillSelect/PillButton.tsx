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
}

export const PillButton: React.FC<React.PropsWithChildren<PillButtonProps>> = ({
  children,
  active,
  variant = "grey",
  ...buttonProps
}) => {
  const buttonClassName = classNames(
    styles.button,
    {
      [styles.active]: active,
    },
    buttonProps.disabled ? styles.disabled : STYLES_BY_VARIANT[variant],
    buttonProps.className
  );

  return (
    <button type="button" {...buttonProps} className={buttonClassName}>
      <Text as="span" size="xs" className={styles.text}>
        {children}
      </Text>
      <FontAwesomeIcon icon={faCaretDown} />
    </button>
  );
};
