import { ComponentStory, ComponentMeta } from "@storybook/react";

import ServiceForm from "./ServiceForm";

export default {
  title: "Views/ServiceForm",
  component: ServiceForm,
} as ComponentMeta<typeof ServiceForm>;

const Template: ComponentStory<typeof ServiceForm> = (args) => (
  <ServiceForm {...args} />
);

export const Source = Template.bind({});
Source.args = {
  formType: "source",
  availableServices: [],
  specifications: {
    type: "object",
  },
};
