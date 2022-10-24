import { faCaretDown, faCaretUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { Text } from "../Text";
import styles from "./PillButton.module.scss";

interface PillButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asDropdown?: boolean;
  active?: boolean;
}

export const PillButton: React.FC<React.PropsWithChildren<PillButtonProps>> = ({
  children,
  active,
  asDropdown,
  ...buttonProps
}) => {
  const buttonClassName = classNames(
    styles.button,
    {
      [styles.active]: active,
      // TODO: Implement tint styles
    },
    buttonProps.className
  );

  return (
    <button {...buttonProps} className={buttonClassName}>
      <Text as="span" size="xs">
        {children}
      </Text>
      {asDropdown && <FontAwesomeIcon icon={active ? faCaretUp : faCaretDown} className={styles.caret} />}
    </button>
  );
};
