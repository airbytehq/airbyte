import { faCaretDown, faCaretUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { Text } from "../Text";
import styles from "./PillButton.module.scss";

interface PillButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  withCaret?: boolean;
  isActive?: boolean;
  light: boolean;
}

export const PillButton: React.FC<React.PropsWithChildren<PillButtonProps>> = ({
  children,
  isActive,
  withCaret,
  light,
  ...buttonProps
}) => {
  return (
    <button
      {...buttonProps}
      className={classNames(
        styles.button,
        {
          [styles.active]: isActive,
          [styles.light]: light,
        },
        buttonProps.className
      )}
    >
      <Text as="span" size="xs">
        {children}
      </Text>
      {withCaret && <FontAwesomeIcon icon={isActive ? faCaretUp : faCaretDown} className={styles.caret} />}
    </button>
  );
};
