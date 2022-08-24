import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Tooltip } from "./Tooltip";
import { TooltipLearnMoreLink } from "./TooltipLearnMoreLink";
import { TooltipTable } from "./TooltipTable";

export default {
  title: "Ui/Tooltip",
  component: Tooltip,
  argTypes: {
    control: { type: { name: "string", required: true } },
    children: { type: { name: "string", required: true } },
  },
} as ComponentMeta<typeof Tooltip>;

const Template: ComponentStory<typeof Tooltip> = (args) => (
  <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center" }}>
    <Tooltip {...args} />
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

export const WithLearnMoreUrl = Template.bind({});
WithLearnMoreUrl.args = {
  control: "Hover to see Tooltip with Body",
  children: (
    <>
      Airbyte is hiring! <TooltipLearnMoreLink url="https://www.airbyte.com/careers" />
    </>
  ),
};

export const WithTable = Template.bind({});
WithTable.args = {
  control: "Hover to see Tooltip with Table",
  children: (
    <TooltipTable
      rows={[
        ["String", "Value"],
        ["Number", 32768],
        ["With a longer label", "And here is a longer value"],
      ]}
    />
  ),
};
