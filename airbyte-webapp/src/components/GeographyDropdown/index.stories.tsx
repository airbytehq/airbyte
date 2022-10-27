import { ComponentStory, ComponentMeta } from "@storybook/react";

import { GeographyDropdown } from "./GeographyDropdown";

export default {
  title: "Ui/GeographyDropdown",
  component: GeographyDropdown,
} as ComponentMeta<typeof GeographyDropdown>;

const Template: ComponentStory<typeof GeographyDropdown> = (args) => <GeographyDropdown {...args} />;

export const Primary = Template.bind({});
Primary.args = {};
