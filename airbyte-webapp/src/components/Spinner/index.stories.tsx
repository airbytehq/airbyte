import { ComponentStory, ComponentMeta } from "@storybook/react";

import SpinnerComponent from "./Spinner";

export default {
  title: "Ui/Spinner",
  component: SpinnerComponent,
  argTypes: {
    small: { type: "boolean", required: false },
  },
} as ComponentMeta<typeof SpinnerComponent>;

const Template: ComponentStory<typeof SpinnerComponent> = (args) => <SpinnerComponent {...args} />;

export const Primary = Template.bind({});
