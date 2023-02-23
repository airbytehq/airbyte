import { faEye } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { useMemo, useRef } from "react";
import { FormattedMessage } from "react-intl";
import { useToggle, useUpdateEffect } from "react-use";

import styles from "./SecretTextArea.module.scss";
import { TextInputContainer, TextInputContainerProps } from "../TextInputContainer";

interface SecretTextAreaProps
  extends Omit<TextInputContainerProps, "onFocus" | "onBlur">,
    React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const SecretTextArea: React.FC<SecretTextAreaProps> = ({
  name,
  disabled,
  value,
  onMouseUp,
  onBlur,
  error,
  light,
  ...textAreaProps
}) => {
  const hasValue = useMemo(() => !!value && String(value).trim().length > 0, [value]);
  const [isContentVisible, toggleIsContentVisible] = useToggle(!hasValue);
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null);
  const textAreaHeightRef = useRef<number>((textAreaProps.rows ?? 1) * 20 + 14);

  useUpdateEffect(() => {
    if (isContentVisible && textAreaRef.current) {
      textAreaRef.current.focus();
      const selectionStart = value ? String(value).length : 0;
      textAreaRef.current.setSelectionRange(selectionStart, selectionStart);
    }
  }, [isContentVisible]);

  return (
    <TextInputContainer disabled={disabled} error={error} light={light}>
      {isContentVisible ? (
        <textarea
          spellCheck={false}
          {...textAreaProps}
          className={classNames(styles.textarea, "fs-exclude", textAreaProps.className)}
          name={name}
          disabled={disabled}
          ref={textAreaRef}
          onMouseUp={(event) => {
            textAreaHeightRef.current = textAreaRef.current?.offsetHeight ?? textAreaHeightRef.current;
            onMouseUp?.(event);
          }}
          onBlur={(event) => {
            textAreaHeightRef.current = textAreaRef.current?.offsetHeight ?? textAreaHeightRef.current;
            if (hasValue) {
              toggleIsContentVisible();
            }
            onBlur?.(event);
          }}
          style={{ height: textAreaHeightRef.current }}
          value={value}
          data-testid="secretTextArea-textarea"
        />
      ) : (
        <>
          <button
            type="button"
            className={styles.toggleVisibilityButton}
            onClick={() => {
              toggleIsContentVisible();
            }}
            style={{
              height: textAreaHeightRef.current,
            }}
            disabled={disabled}
            data-testid="secretTextArea-visibilityButton"
          >
            <FontAwesomeIcon icon={faEye} fixedWidth /> <FormattedMessage id="ui.secretTextArea.hidden" />
          </button>
          <input
            type="password"
            name={name}
            disabled
            value={value}
            className={styles.passwordInput}
            readOnly
            aria-hidden
            data-testid="secretTextArea-input"
          />
        </>
      )}
    </TextInputContainer>
  );
};
