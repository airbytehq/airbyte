import { ComponentStory, ComponentMeta } from "@storybook/react";
import React from "react";

import Button from "../Button";
import { Popout } from "./Popout";

export default {
  title: "Ui/Popout",
  component: Popout,
} as ComponentMeta<typeof Popout>;

const Target: React.FC<{ onOpen: () => void; title: string }> = ({ onOpen, title }) => {
  return <Button onClick={() => onOpen()}>{title}</Button>;
};

const options = [
  {
    value: 1,
    label: "Test 1",
  },
  {
    value: 2,
    label: "Test 2",
  },
  {
    value: 3,
    label: "Test 3",
  },
];

const Template: ComponentStory<typeof Popout> = (args) => (
  <Popout
    {...args}
    options={options}
    targetComponent={(targetProps) => (
      <Target onOpen={targetProps.onOpen} title={`isSearchable: ${args.isSearchable}`} />
    )}
  />
);

export const Example = Template.bind({});
Example.args = {
  children: "Text",
  title: "Title",
  isSearchable: false,
};
