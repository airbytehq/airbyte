import { KeyboardEventHandler, useState } from "react";
import { OnChangeValue } from "react-select";
import CreatableSelect from "react-select/creatable";

const components = {
  DropdownIndicator: null,
};

interface Tag {
  readonly id: string;
  readonly value: string;
}

interface NewTagInputProps {
  name: string;
  value: string[];
  onChange: (value: string[]) => void;
}
// TODO: what happens if there are two tags with the same text?
export const NewTagInput: React.FC<NewTagInputProps> = ({ onChange, value, name }) => {
  const tags = value.map((value) => ({ id: value, value }));
  // input value is a tag draft
  const [inputValue, setInputValue] = useState("");

  // handle when an item is created
  const handleChange = (value: OnChangeValue<Tag, true>) => {
    onChange(value.map((item) => item.value));
    // todo: should also handle splitting up pasted strings by delimiters
    //
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
        onChange([...value, inputValue]);
        // todo: do i need to manually clear the input
        event.preventDefault();
    }
  };

  // todo: helpful placeholder
  return (
    <CreatableSelect
      name={name}
      components={components}
      inputValue={inputValue}
      isClearable
      isMulti
      menuIsOpen={false}
      onChange={handleChange}
      onInputChange={handleInputChange}
      onKeyDown={handleKeyDown}
      placeholder=""
      value={tags}
    />
  );
};
