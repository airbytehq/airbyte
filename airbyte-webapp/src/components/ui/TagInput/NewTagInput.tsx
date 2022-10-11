import { uniqueId } from "lodash";
import { KeyboardEventHandler, useMemo, useState } from "react";
import { ActionMeta, MultiValue, OnChangeValue } from "react-select";
import CreatableSelect from "react-select/creatable";

const components = {
  DropdownIndicator: null,
};

const customStyles = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- react-select's typing is lacking here
  multiValue: (provided: any) => ({
    ...provided,
    maxWidth: "100%",
    display: "flex",
    background: "#262963", // colors.$dark-blue-800
    color: "white", // colors.$white
    borderRadius: "4px", // variables.$border-radius-sm
    paddingLeft: "5px", // variables.$spacing-sm
  }),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- same as above
  multiValueLabel: (provided: any) => ({
    ...provided,
    color: "white",
    fontWeight: 500,
  }),
};

interface Tag {
  readonly label: string;
  readonly value: string;
}

interface NewTagInputProps {
  name: string;
  fieldValue: string[];
  onChange: (value: string[]) => void;
  error?: boolean;
  disabled?: boolean;
}

const generateTagFromString = (inputValue: string): Tag => ({
  label: inputValue,
  value: uniqueId(`tag_value_`),
});

const generateStringFromTag = (tag: Tag): string => tag.label;

const delimiters = [",", ";"];

export const NewTagInput: React.FC<NewTagInputProps> = ({ onChange, fieldValue, name, disabled }) => {
  const tags = useMemo(() => fieldValue.map(generateTagFromString), [fieldValue]);

  // input value is a tag draft
  const [inputValue, setInputValue] = useState("");

  const handleDelete = (_value: OnChangeValue<Tag, true>, actionMeta: ActionMeta<Tag>) => {
    let updatedTags: MultiValue<Tag> = tags;
    /**
     * remove-value: user clicked x to remove tag
     * clear: user clicked big x to clear all tags
     * pop-value: user clicked backspace to remove tag
     */
    // TODO: handle deletes by selecting tag and hitting space/enter/delete
    // OR do not highlight the delete button when selecting a tag?
    if (actionMeta.action === "remove-value") {
      updatedTags = updatedTags.filter((tag) => tag.value !== actionMeta.removedValue.value);
    } else if (actionMeta.action === "clear") {
      updatedTags = [];
    } else if (actionMeta.action === "pop-value") {
      updatedTags = updatedTags.slice(0, updatedTags.length - 1);
      console.log({ updatedTags });
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
      case ",":
      case "Tab":
        inputValue.trim().length > 1 && onChange([...fieldValue, inputValue.trim()]);

        event.preventDefault();
        setInputValue("");
    }
  };

  // todo: helper text? tootlip?
  return (
    <CreatableSelect
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
      placeholder=""
      value={tags}
      isDisabled={disabled}
      styles={customStyles}
    />
  );
};
