import { faCaretDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { Text } from "../Text";
import styles from "./PillButton.module.scss";

interface PillButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
}

export const PillButton: React.FC<React.PropsWithChildren<PillButtonProps>> = ({
  children,
  active,
  ...buttonProps
}) => {
  const buttonClassName = classNames(
    styles.button,
    {
      [styles.active]: active,
    },
    buttonProps.className
  );

  return (
    <button {...buttonProps} className={buttonClassName}>
      <Text as="span" size="xs" className={styles.text}>
        {children}
      </Text>
      <FontAwesomeIcon icon={faCaretDown} />
    </button>
  );
};
