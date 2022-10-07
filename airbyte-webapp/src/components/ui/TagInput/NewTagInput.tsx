import { uniqueId } from "lodash";
import { KeyboardEventHandler, useState } from "react";
import { ActionMeta, MultiValue, OnChangeValue } from "react-select";
import CreatableSelect from "react-select/creatable";

const components = {
  DropdownIndicator: null,
};

interface Tag {
  readonly id: string;
  readonly label: string;
}

interface NewTagInputProps {
  name: string;
  value: MultiValue<Tag>;
  onChange: (value: MultiValue<Tag>) => void;
  error?: boolean;
  disabled?: boolean;
}

// TODO: defaultValue, child component doing crummy stuff with keys
export const NewTagInput: React.FC<NewTagInputProps> = ({ onChange, value: fieldValue, name, disabled }) => {
  const generateTag = (inputValue: string) => ({ id: uniqueId(`tag_`), label: inputValue });
  // give each tag a unique id
  const tags = fieldValue;
  // input value is a tag draft
  const [inputValue, setInputValue] = useState("");

  // handle when an item is created
  const handleChange = (value: OnChangeValue<Tag, true>, actionMeta: ActionMeta<Tag>) => {
    // the value should always contain just the value, not the id
    let newTags: MultiValue<Tag> = tags;
    if (actionMeta.action === "remove-value") {
      newTags = tags.filter((tag) => tag.id !== actionMeta.removedValue.id);
    } else if (actionMeta.action === "clear") {
      newTags = [];
    }
    onChange(newTags);
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
        const newTag = generateTag(inputValue);
        onChange([...fieldValue, newTag]);
        // todo: do i need to manually clear the input
        event.preventDefault();
        setInputValue("");
    }
  };

  // todo: helpful placeholder!
  return (
    <CreatableSelect
      name={name}
      components={components}
      inputValue={inputValue}
      isClearable
      isMulti
      // todo: is this actually what we want on blur?
      onBlur={() => handleChange}
      menuIsOpen={false}
      onChange={handleChange}
      onInputChange={handleInputChange}
      onKeyDown={handleKeyDown}
      placeholder=""
      value={tags}
      isDisabled={disabled}
    />
  );
};
