import { ComponentStory, ComponentMeta } from "@storybook/react";

import { CodeEditor } from "./CodeEditor";

export default {
  title: "UI/CodeEditor",
  component: CodeEditor,
  argTypes: {},
} as ComponentMeta<typeof CodeEditor>;

const Template: ComponentStory<typeof CodeEditor> = (args) => <CodeEditor {...args} />;

const code = `{
  "name": "Airbyte",
  "about": "Open-source data integration for the modern data stack",
  "url": "https://airbyte.com",
}`;

export const Primary = Template.bind({});
Primary.args = {
  value: code,
  language: "json",
};
