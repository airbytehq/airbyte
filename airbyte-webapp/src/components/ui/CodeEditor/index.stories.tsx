import { ComponentStory, ComponentMeta } from "@storybook/react";

import { CodeEditor } from "./CodeEditor";

export default {
  title: "UI/CodeEditor",
  component: CodeEditor,
  argTypes: {},
} as ComponentMeta<typeof CodeEditor>;

const Template: ComponentStory<typeof CodeEditor> = (args) => <CodeEditor {...args} />;

const code = `
if __name__ == "__main__":
  print("Hello, Airbyte!")
`;

export const Primary = Template.bind({
  code,
  language: "python",
});
