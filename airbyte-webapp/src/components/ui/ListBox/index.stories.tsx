import { ComponentMeta } from "@storybook/react";
import { useState } from "react";

import { ListBox } from "./ListBox";

const listOptions = [
  {
    label: "one",
    value: 1,
  },
  {
    label: "two",
    value: 2,
  },
  {
    label: "three",
    value: 3,
  },
];

export default {
  title: "Ui/ListBox",
  component: ListBox,
  argTypes: {
    options: listOptions,
  },
} as ComponentMeta<typeof ListBox>;

export const Primary = () => {
  const [selectedOption, setSelectedOption] = useState(1);

  return <ListBox options={listOptions} selectedValue={selectedOption} onSelect={setSelectedOption} />;
};
