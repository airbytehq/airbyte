import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Spinner } from "./Spinner";

export default {
  title: "UI/Spinner",
  component: Spinner,
  argTypes: {
    small: { type: "boolean", required: false },
  },
} as ComponentMeta<typeof Spinner>;

const Template: ComponentStory<typeof Spinner> = (args) => <Spinner {...args} />;

export const Primary = Template.bind({});
