import { uniqueId } from "lodash";
import { KeyboardEventHandler, useMemo, useState } from "react";
import { ActionMeta, MultiValue, OnChangeValue } from "react-select";
import CreatableSelect from "react-select/creatable";

import styles from "./TagInput.module.scss";

const components = {
  DropdownIndicator: null,
};

const customStyles = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- react-select's typing is lacking here
  multiValue: (provided: any) => ({
    ...provided,
    maxWidth: "100%",
    display: "flex",
    background: `${styles.backgroundColor}`,
    color: `${styles.fontColor}`,
    borderRadius: `${styles.borderRadius}`,
    paddingLeft: `${styles.paddingLeft}`,
  }),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- same as above
  multiValueLabel: (provided: any) => ({
    ...provided,
    color: `${styles.fontColor}`,
    fontWeight: 500,
  }),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- same as above
  multiValueRemove: (provided: any) => ({
    ...provided,
    borderRadius: `${styles.borderRadius}`,
  }),
};

interface Tag {
  readonly label: string;
  readonly value: string;
}

interface TagInputProps {
  name: string;
  fieldValue: string[];
  onChange: (value: string[]) => void;
  error?: boolean;
  disabled?: boolean;
  id?: string;
}

const generateTagFromString = (inputValue: string): Tag => ({
  label: inputValue,
  value: uniqueId(`tag_value_`),
});

const generateStringFromTag = (tag: Tag): string => tag.label;

const delimiters = [",", ";"];

export const TagInput: React.FC<TagInputProps> = ({ onChange, fieldValue, name, disabled, id }) => {
  const tags = useMemo(() => fieldValue.map(generateTagFromString), [fieldValue]);

  // input value is a tag draft
  const [inputValue, setInputValue] = useState("");

  // handles various ways of deleting a value
  const handleDelete = (_value: OnChangeValue<Tag, true>, actionMeta: ActionMeta<Tag>) => {
    let updatedTags: MultiValue<Tag> = tags;

    /**
     * remove-value: user clicked x or used backspace/delete to remove tag
     * clear: user clicked big x to clear all tags
     * pop-value: user clicked backspace to remove tag
     */
    if (actionMeta.action === "remove-value") {
      updatedTags = updatedTags.filter((tag) => tag.value !== actionMeta.removedValue.value);
    } else if (actionMeta.action === "clear") {
      updatedTags = [];
    } else if (actionMeta.action === "pop-value") {
      updatedTags = updatedTags.slice(0, updatedTags.length - 1);
    }
    onChange(updatedTags.map((tag) => generateStringFromTag(tag)));
  };

  // handle when a user types OR pastes in the input
  const handleInputChange = (inputValue: string) => {
    setInputValue(inputValue);

    delimiters.forEach((delimiter) => {
      if (inputValue.includes(delimiter)) {
        const newTagStrings = inputValue
          .split(delimiter)
          .map((tag) => tag.trim())
          .filter(Boolean);

        inputValue.trim().length > 1 && onChange([...fieldValue, ...newTagStrings]);
        setInputValue("");
      }
    });
  };

  // handle when user presses keyboard keys in the input
  const handleKeyDown: KeyboardEventHandler<HTMLDivElement> = (event) => {
    if (!inputValue || !inputValue.length) {
      return;
    }
    switch (event.key) {
      case "Enter":
      case "Tab":
        inputValue.trim().length > 1 && onChange([...fieldValue, inputValue.trim()]);

        event.preventDefault();
        setInputValue("");
    }
  };

  return (
    <div data-testid="tag-input">
      <CreatableSelect
        inputId={id}
        name={name}
        components={components}
        inputValue={inputValue}
        isClearable
        isMulti
        onBlur={() => handleDelete}
        menuIsOpen={false}
        onChange={handleDelete}
        onInputChange={handleInputChange}
        onKeyDown={handleKeyDown}
        value={tags}
        isDisabled={disabled}
        styles={customStyles}
      />
    </div>
  );
};
