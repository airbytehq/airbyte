import { faEye, faEyeSlash } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useEffect, useRef } from "react";
import { useIntl } from "react-intl";
import { useToggle } from "react-use";
import styled from "styled-components";
import { Theme } from "theme";

import Button from "../Button";

type IStyleProps = InputProps & { theme: Theme };

const getBackgroundColor = (props: IStyleProps) => {
  if (props.error) {
    return props.theme.greyColor10;
  } else if (props.light) {
    return props.theme.whiteColor;
  }

  return props.theme.greyColor0;
};

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  light?: boolean;
  defaultFocus?: boolean;
}

const InputContainer = styled.div<InputProps>`
  width: 100%;
  position: relative;
  background: ${(props) => getBackgroundColor(props)};
  border: 1px solid ${(props) => (props.error ? props.theme.dangerColor : props.theme.greyColor0)};
  border-radius: 4px;

  ${({ disabled, theme, light, error }) =>
    !disabled &&
    `
      &:hover {
        background: ${light ? theme.whiteColor : theme.greyColor20};
        border-color: ${error ? theme.dangerColor : theme.greyColor20};
      }
    `}

  &.input-container--focused {
    background: ${({ theme, light }) => (light ? theme.whiteColor : theme.primaryColor12)};
    border-color: ${({ theme }) => theme.primaryColor};
  }
`;

const InputComponent = styled.input<InputProps & { isPassword?: boolean }>`
  outline: none;
  width: ${({ isPassword, disabled }) => (isPassword && !disabled ? "calc(100% - 22px)" : "100%")};
  padding: 7px 8px 7px 8px;
  font-size: 14px;
  line-height: 20px;
  font-weight: normal;
  border: none;
  background: none;
  color: ${({ theme }) => theme.textColor};
  caret-color: ${({ theme }) => theme.primaryColor};

  &::placeholder {
    color: ${({ theme }) => theme.greyColor40};
  }

  &:disabled {
    pointer-events: none;
    color: ${({ theme }) => theme.greyColor55};
  }
`;

const VisibilityButton = styled(Button)`
  position: absolute;
  right: 0px;
  top: 0;
  display: flex;
  height: 100%;
  width: 30px;
  align-items: center;
  justify-content: center;
  border: none;
`;

const Input: React.FC<InputProps> = (props) => {
  const { defaultFocus = false } = props;

  const { formatMessage } = useIntl();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isContentVisible, setIsContentVisible] = useToggle(false);
  const [focused, toggleFocused] = useToggle(false);

  const isPassword = props.type === "password";
  const isVisibilityButtonVisible = isPassword && !props.disabled;
  const type = isPassword ? (isContentVisible ? "text" : "password") : props.type;
  const onInputFocusChange = () => toggleFocused();

  useEffect(() => {
    if (defaultFocus && inputRef.current !== null) {
      inputRef.current.focus();
    }
  }, [inputRef, defaultFocus]);

  return (
    <InputContainer {...props} className={focused ? "input-container--focused" : undefined}>
      <InputComponent
        {...props}
        ref={inputRef}
        type={type}
        isPassword={isPassword}
        onFocus={onInputFocusChange}
        onBlur={onInputFocusChange}
        data-testid="input"
      />
      {isVisibilityButtonVisible ? (
        <VisibilityButton
          iconOnly
          onClick={() => setIsContentVisible()}
          type="button"
          aria-label={formatMessage({
            id: `ui.input.${isContentVisible ? "hide" : "show"}Password`,
          })}
          data-testid="toggle-password-visibility-button"
        >
          <FontAwesomeIcon icon={isContentVisible ? faEyeSlash : faEye} fixedWidth />
        </VisibilityButton>
      ) : null}
    </InputContainer>
  );
};

export default Input;
export { Input };
