import React, { useRef, useState } from "react";
import styled from "styled-components";

import TagItem, { IItemProps } from "./TagItem";

const MainContainer = styled.div<{ error?: boolean }>`
  width: 100%;
  min-height: 36px;
  background: ${({ theme }) => theme.whiteColor};
  border-radius: 4px;
  padding: 6px 6px 0;
  cursor: text;
  max-height: 100%;
  overflow: auto;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-self: stretch;
  border: 1px solid
    ${({ theme, error }) => (error ? theme.dangerColor : theme.whiteColor)};
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
  &::placeholder {
    color: ${({ theme }) => theme.greyColor40};
  }
`;

type IProps = {
  inputProps: React.InputHTMLAttributes<HTMLInputElement>;
  value: Array<IItemProps>;
  className?: string;
  validationRegex?: RegExp;
  error?: boolean;
  addOnBlur?: boolean;

  onEnter: (value?: string | number | readonly string[]) => void;
  onDelete: (value: string) => void;
  onError?: () => void;
};

const TagInput: React.FC<IProps> = ({
  inputProps,
  onEnter,
  value,
  className,
  onDelete,
  validationRegex,
  error,
  onError,
  addOnBlur,
}) => {
  const inputElement = useRef<HTMLInputElement | null>(null);
  const [selectedElement, setSelectedElement] = useState("");

  const handleContainerBlur = () => setSelectedElement("");
  const handleContainerClick = () => {
    if (inputElement.current !== null) {
      inputElement.current.focus();
    }
  };

  const onAddValue = () => {
    if (inputElement.current?.value) {
      return;
    }

    const isValid = validationRegex
      ? !!inputElement.current?.value.match(validationRegex)
      : true;

    if (isValid) {
      onEnter(inputProps.value);
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
    } else if ((keyCode === 46 || keyCode === 8) && inputProps.value === "") {
      if (selectedElement) {
        const nextId = value.length - 1 > 0 ? value[value.length - 2].id : "";
        onDelete(selectedElement);
        setSelectedElement(nextId);
      } else if (value.length) {
        setSelectedElement(value[value.length - 1].id);
      }
    }
  };

  const handleInputBlur = () => {
    if (addOnBlur) {
      onAddValue();
    }
  };

  const inputPlaceholder =
    !value.length && inputProps.placeholder ? inputProps.placeholder : "";

  return (
    <MainContainer
      onBlur={handleContainerBlur}
      onClick={handleContainerClick}
      className={className}
      error={error}
    >
      {value.map((item, key) => (
        <TagItem
          disabled={inputProps.disabled}
          key={`tag-${key}`}
          item={item}
          onDeleteTag={onDelete}
          isSelected={item.id === selectedElement}
        />
      ))}
      <InputElement
        {...inputProps}
        autoComplete={"off"}
        placeholder={inputPlaceholder}
        ref={inputElement}
        onBlur={handleInputBlur}
        onKeyDown={handleInputKeyDown}
        onChange={(event) => {
          setSelectedElement("");
          inputProps?.onChange?.(event);
        }}
      />
    </MainContainer>
  );
};

export default TagInput;
