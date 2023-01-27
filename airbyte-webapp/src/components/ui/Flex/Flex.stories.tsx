import { ComponentStory, ComponentMeta } from "@storybook/react";

import { FlexContainer } from "./FlexContainer";
import { FlexItem } from "./FlexItem";

export default {
  title: "Ui/Flex",
  component: FlexContainer,
} as ComponentMeta<typeof FlexContainer>;

const Template: ComponentStory<typeof FlexContainer> = (args) => <FlexContainer {...args} />;

const Item = ({ label, grow }: { label: string; grow?: boolean }) => (
  <FlexItem grow={grow} style={{ backgroundColor: "#dddddd", borderRadius: 5, padding: 20 }}>{`<FlexItem${
    grow ? " grow" : ""
  }>${label}</FlexItem>`}</FlexItem>
);

export const NoGrow = Template.bind({});
NoGrow.args = {
  children: (
    <>
      <Item label="first" />
      <Item label="second with a lot of content" />
      <Item label="third" />
      <Item label="forth" />
    </>
  ),
};

export const Grow = Template.bind({});
Grow.args = {
  children: (
    <>
      <Item label="first" grow />
      <Item label="second" />
    </>
  ),
};
