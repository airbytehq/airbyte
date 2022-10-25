import { ComponentStory, ComponentMeta } from "@storybook/react";

import { PillSelect } from "./PillSelect";

export default {
  title: "UI/PillSelect",
  component: PillSelect,
} as ComponentMeta<typeof PillSelect>;

const Template: ComponentStory<typeof PillSelect> = (args) => (
  <div style={{ width: "120px" }}>
    <PillSelect {...args} />
  </div>
);

const options = [
  {
    value: "id",
    label: "id",
  },
  {
    value: "first_name",
    label: "first_name",
  },
  {
    value: "last_name",
    label: "last_name",
  },
  {
    value: "email",
    label: "email",
  },
  {
    value: "company",
    label: "company",
  },
];

export const Primary = Template.bind({});
Primary.args = {
  options,
  value: "email",
};

export const Multi = Template.bind({});
Multi.args = {
  options,
  isMulti: true,
  value: ["first_name", "last_name"],
};
