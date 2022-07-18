import { ComponentStory, ComponentMeta } from "@storybook/react";

import { ToolTip } from "./ToolTip";

export default {
  title: "Ui/ToolTip",
  component: ToolTip,
  argTypes: {
    control: { type: { name: "string", required: true } },
    children: { type: { name: "string", required: true } },
  },
} as ComponentMeta<typeof ToolTip>;

const Template: ComponentStory<typeof ToolTip> = (args) => (
  <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center" }}>
    <ToolTip {...args} />
  </div>
);

export const Primary = Template.bind({});
Primary.args = {
  control: "Hover to see Tooltip",
  children: (
    <>
      Looking for a job?{" "}
      <a href="https://www.airbyte.com/careers" target="_blank" rel="noreferrer">
        Apply at Airbyte!
      </a>
    </>
  ),
};
