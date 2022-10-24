import { ComponentStory, ComponentMeta } from "@storybook/react";
import React from "react";

import { Button } from "../Button";
import { PillButton } from "../PillButton";
import { Popout } from "./Popout";

export default {
  title: "Ui/Popout",
  component: Popout,
} as ComponentMeta<typeof Popout>;

const ButtonTarget: React.FC<{ onOpen: () => void; title: string }> = ({ onOpen, title }) => {
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
      <ButtonTarget onOpen={targetProps.onOpen} title={`isSearchable: ${args.isSearchable}`} />
    )}
  />
);

const PillButtonTemplate: ComponentStory<typeof Popout> = (args) => (
  <Popout
    {...args}
    options={options}
    targetComponent={(targetProps) => (
      <PillButton asDropdown onClick={() => targetProps.onOpen()} active={targetProps.isOpen}>
        {args.title}
      </PillButton>
    )}
  />
);

export const Primary = Template.bind({});
Primary.args = {
  title: "Title",
  isSearchable: false,
};

export const WithPillButton = PillButtonTemplate.bind({});
WithPillButton.args = {
  title: "With PillButton",
};
