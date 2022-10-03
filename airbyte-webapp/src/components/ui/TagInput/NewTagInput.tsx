import { KeyboardEventHandler, useState } from "react";
import { MultiValue, OnChangeValue } from "react-select";
import CreatableSelect from "react-select/creatable";

const components = {
  DropdownIndicator: null,
};

interface Tag {
  readonly id: string;
  readonly value: string;
}

interface NewTagInputProps {
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
}

export const NewTagInput: React.FC<NewTagInputProps> = ({ inputProps }) => {
  const [tags, setTags] = useState<MultiValue<Tag>>([]);
  // input value is a tag draft
  const [inputValue, setInputValue] = useState("");

  const createTag = (id: string) => ({
    id,
    value: id,
  });

  // handle when an item is created
  const handleChange = (value: OnChangeValue<Tag, true>) => {
    setTags(value);
    // todo: should also handle splitting up pasted strings by delimiters
  };

  // handle when a user types OR pastes in a value
  const handleInputChange = (inputValue: string) => {
    setInputValue(inputValue);
  };

  // handle when user types in the input
  const handleKeyDown: KeyboardEventHandler<HTMLDivElement> = (event) => {
    if (!inputValue) {
      return;
    }

    switch (event.key) {
      case "Enter":
      case "Tab":
        setTags([...tags, createTag(inputValue)]);
        // todo: do i need to manually clear the input
        event.preventDefault();
    }
  };

  const inputPlaceholder = !tags.length && inputProps?.placeholder ? inputProps.placeholder : "";

  return (
    <CreatableSelect
      components={components}
      inputValue={inputValue}
      isClearable
      isMulti
      menuIsOpen={false}
      onChange={handleChange}
      onInputChange={handleInputChange}
      onKeyDown={handleKeyDown}
      placeholder={inputPlaceholder}
      value={tags}
    />
  );
};
