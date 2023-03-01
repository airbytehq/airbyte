import { faEye, faEyeSlash } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React, { useCallback, useRef, useState } from "react";
import { useIntl } from "react-intl";
import { useToggle } from "react-use";

import Button from "../Button";
import styles from "./Input.module.scss";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  light?: boolean;
  focusedStyle?: boolean;
  grey?: boolean;
}

export const Input: React.FC<InputProps> = ({ light, error, grey, focusedStyle, ...props }) => {
  const { formatMessage } = useIntl();

  const inputRef = useRef<HTMLInputElement | null>(null);
  const buttonRef = useRef<HTMLButtonElement | null>(null);
  const inputSelectionStartRef = useRef<number | null>(null);

  const [isContentVisible, toggleIsContentVisible] = useToggle(false);
  const [focused, setFocused] = useState(false);

  const isPassword = props.type === "password";
  const isVisibilityButtonVisible = isPassword && !props.disabled;
  const type = isPassword ? (isContentVisible ? "text" : "password") : props.type;

  const focusOnInputElement = useCallback(() => {
    if (!inputRef.current) {
      return;
    }

    const { current: element } = inputRef;
    const selectionStart = inputSelectionStartRef.current ?? inputRef.current?.value.length;

    element.focus();

    if (selectionStart) {
      // Update input cursor position to where it was before
      window.setTimeout(() => {
        element.setSelectionRange(selectionStart, selectionStart);
      }, 0);
    }
  }, []);

  const onContainerFocus: React.FocusEventHandler<HTMLDivElement> = () => {
    setFocused(true);
  };

  const onContainerBlur: React.FocusEventHandler<HTMLDivElement> = (event) => {
    if (isVisibilityButtonVisible && event.target === inputRef.current) {
      // Save the previous selection
      inputSelectionStartRef.current = inputRef.current.selectionStart;
    }

    setFocused(false);

    if (isPassword) {
      window.setTimeout(() => {
        if (document.activeElement !== inputRef.current && document.activeElement !== buttonRef.current) {
          toggleIsContentVisible(false);
          inputSelectionStartRef.current = null;
        }
      }, 0);
    }
  };

  return (
    <div
      className={classNames(styles.container, {
        [styles.disabled]: props.disabled,
        [styles.focused]: focused && focusedStyle,
        [styles.light]: light,
        [styles.error]: error,
        [styles.grey]: grey,
      })}
      data-testid="input-container"
      onFocus={onContainerFocus}
      onBlur={onContainerBlur}
    >
      <input
        data-testid="input"
        {...props}
        ref={inputRef}
        type={type}
        className={classNames(
          styles.input,
          {
            [styles.disabled]: props.disabled,
            [styles.password]: isPassword,
          },
          props.className
        )}
      />
      {isVisibilityButtonVisible ? (
        <Button
          className={styles.visibilityButton}
          ref={buttonRef}
          iconOnly
          onClick={() => {
            toggleIsContentVisible();
            focusOnInputElement();
          }}
          type="button"
          aria-label={formatMessage({
            id: `ui.input.${isContentVisible ? "hide" : "show"}Password`,
          })}
          data-testid="toggle-password-visibility-button"
        >
          <FontAwesomeIcon icon={isContentVisible ? faEyeSlash : faEye} fixedWidth />
        </Button>
      ) : null}
    </div>
  );
};

export default Input;
