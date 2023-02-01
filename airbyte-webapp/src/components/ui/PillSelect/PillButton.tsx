import { faCaretDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Children } from "react";

import styles from "./PillButton.module.scss";
import { Text } from "../Text";

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
  hasError?: boolean;
}

export const PillButton: React.FC<PillButtonProps> = ({
  children,
  active,
  variant = "grey",
  hasError = false,
  ...buttonProps
}) => {
  const buttonClassName = classNames(
    styles.button,
    {
      [styles.active]: active,
      [styles.disabled]: buttonProps.disabled,
    },
    STYLES_BY_VARIANT[hasError ? "strong-red" : variant],
    buttonProps.className
  );
  const arrayChildren = Children.toArray(children);

  return (
    <button type="button" {...buttonProps} className={buttonClassName}>
      {Children.map(arrayChildren, (child, index) => (
        <>
          <div key={index} className={styles.labelContainer}>
            <Text as="span" size="xs" className={styles.text}>
              {child}
            </Text>
          </div>
          {index !== arrayChildren?.length - 1 && <div className={styles.divider} />}
        </>
      ))}
      <FontAwesomeIcon className={styles.icon} icon={faCaretDown} />
    </button>
  );
};
