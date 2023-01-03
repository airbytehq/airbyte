import classNames from "classnames";
import { useState } from "react";

import styles from "./TextInputContainer.module.scss";

export interface TextInputContainerProps {
  disabled?: boolean;
  light?: boolean;
  error?: boolean;
  onFocus?: React.FocusEventHandler<HTMLDivElement>;
  onBlur?: React.FocusEventHandler<HTMLDivElement>;
}

export const TextInputContainer: React.FC<React.PropsWithChildren<TextInputContainerProps>> = ({
  disabled,
  light,
  error,
  onFocus,
  onBlur,
  children,
}) => {
  const [focused, setFocused] = useState(false);

  return (
    <div
      className={classNames(styles.container, {
        [styles.disabled]: disabled,
        [styles.focused]: focused,
        [styles.light]: light,
        [styles.error]: error,
      })}
      onFocus={(event) => {
        setFocused(true);
        onFocus?.(event);
      }}
      onBlur={(event) => {
        setFocused(false);
        onBlur?.(event);
      }}
      data-testid="textInputContainer"
    >
      {children}
    </div>
  );
};
