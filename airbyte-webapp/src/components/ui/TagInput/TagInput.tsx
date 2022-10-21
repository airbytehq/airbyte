import React, { useRef, useState } from "react";
import styled from "styled-components";

import TagItem, { IItemProps } from "./TagItem";

const MainContainer = styled.div<{ error?: boolean; disabled?: boolean }>`
  width: 100%;
  min-height: 36px;
  border-radius: 4px;
  padding: 6px 6px 0;
  cursor: text;
  max-height: 100%;
  overflow: auto;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-self: stretch;
  border: 1px solid ${(props) => (props.error ? props.theme.dangerColor : props.theme.greyColor0)};
  background: ${(props) => (props.error ? props.theme.greyColor10 : props.theme.greyColor0)};
  caret-color: ${({ theme }) => theme.primaryColor};

  ${({ disabled, theme, error }) =>
    !disabled &&
    `
      &:hover {
        background: ${theme.greyColor20};
        border-color: ${error ? theme.dangerColor : theme.greyColor20};
      }
    `}

  &:focus,
  &:focus-within {
    background: ${({ theme }) => theme.primaryColor12};
    border-color: ${({ theme }) => theme.primaryColor};
  }
`;

const InputElement = styled.input`
  margin-bottom: 4px;
  border: none;
  outline: none;
  font-size: 14px;
  line-height: 20px;
  font-weight: normal;
  color: ${({ theme }) => theme.textColor};
  flex: 1 1 auto;
  background: rgba(0, 0, 0, 0);

  &::placeholder {
    color: ${({ theme }) => theme.greyColor40};
  }
`;

export interface TagInputProps {
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
  value: IItemProps[];
  className?: string;
  validationRegex?: RegExp;
  error?: boolean;
  addOnBlur?: boolean;
  disabled?: boolean;
  name?: string;

  onEnter: (value?: string | number | readonly string[]) => void;
  onDelete: (value: string) => void;
  onError?: () => void;
}

export const TagInput: React.FC<TagInputProps> = ({
  inputProps,
  onEnter,
  value,
  className,
  onDelete,
  validationRegex,
  error,
  disabled,
  onError,
  addOnBlur,
  name,
}) => {
  const inputElement = useRef<HTMLInputElement | null>(null);
  const [selectedElementId, setSelectedElementId] = useState("");
  const [currentInputValue, setCurrentInputValue] = useState("");

  const handleContainerBlur = () => setSelectedElementId("");
  const handleContainerClick = () => {
    if (inputElement.current !== null) {
      inputElement.current.focus();
    }
  };

  const onAddValue = () => {
    if (!inputElement.current?.value) {
      return;
    }

    const isValid = validationRegex ? !!inputElement.current?.value.match(validationRegex) : true;

    if (isValid) {
      onEnter(currentInputValue);
      setCurrentInputValue("");
    } else if (onError) {
      onError();
    }
  };

  const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    const { keyCode } = event;

    // on ENTER click
    if (keyCode === 13) {
      event.stopPropagation();
      event.preventDefault();
      onAddValue();

      // on DELETE or BACKSPACE click when input is empty (select or delete last tag in valuesList)
    } else if ((keyCode === 46 || keyCode === 8) && currentInputValue === "") {
      if (selectedElementId !== "") {
        const nextId = value.length - 1 > 0 ? value[value.length - 2].id : "";
        onDelete(selectedElementId);
        setSelectedElementId(nextId);
      } else if (value.length) {
        setSelectedElementId(value[value.length - 1].id);
      }
    }
  };

  const handleInputBlur = () => {
    if (addOnBlur) {
      onAddValue();
    }
  };

  const inputPlaceholder = !value.length && inputProps?.placeholder ? inputProps.placeholder : "";

  return (
    <MainContainer
      onBlur={handleContainerBlur}
      onClick={handleContainerClick}
      className={className}
      error={error}
      disabled={disabled}
    >
      {value.map((item, key) => (
        <TagItem
          disabled={disabled}
          key={`tag-${key}`}
          item={item}
          onDeleteTag={onDelete}
          isSelected={item.id === selectedElementId}
        />
      ))}
      <InputElement
        {...inputProps}
        name={name}
        disabled={disabled}
        autoComplete="off"
        placeholder={inputPlaceholder}
        ref={inputElement}
        onBlur={handleInputBlur}
        onKeyDown={handleInputKeyDown}
        value={currentInputValue}
        onChange={(event) => {
          setSelectedElementId("");
          setCurrentInputValue(event.target.value);
        }}
      />
    </MainContainer>
  );
};
