import { ComponentStory, ComponentMeta } from "@storybook/react";

import { PillSelect } from "./PillSelect";

export default {
  title: "UI/PillSelect",
  component: PillSelect,
} as ComponentMeta<typeof PillSelect>;

const Template: ComponentStory<typeof PillSelect> = (args) => (
  <div style={{ width: "300px" }}>
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

const optionsWithTwoValues = [
  {
    value: "test1",
    label: ["dog", "cat"],
  },
  {
    value: "test2",
    label: ["dog", "cat", "rat"],
  },
  {
    value: "test3",
    label: "dog",
  },
  {
    value: "test4",
    label: ["cat"],
  },
];

export const PrimaryWithTwoValue = Template.bind({});
PrimaryWithTwoValue.args = {
  options: optionsWithTwoValues,
  value: "test1",
};

export const PrimaryMultiWithTwoValue = Template.bind({});
PrimaryMultiWithTwoValue.args = {
  options: optionsWithTwoValues,
  isMulti: true,
  value: ["test1", "test2"],
};
