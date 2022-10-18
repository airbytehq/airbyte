import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Markdown } from "./Markdown";

export default {
  title: "UI/Markdown",
  component: Markdown,
  argTypes: {},
} as ComponentMeta<typeof Markdown>;

const Template: ComponentStory<typeof Markdown> = (args) => (
  <div style={{ backgroundColor: "white" }}>
    <Markdown {...args} />
  </div>
);

const content = `
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

The quick brown fox jumps over the lazy dog.

  The quick brown fox jumps over the lazy dog.

  > The quick brown fox jumps over the lazy dog.

[Link](https://www.airbyte.com/)

\`Pre\`

*italic*

**bold**

~strikethrough~


\`\`\`javascript
function codeBlock() {
  // comment
}
\`\`\`

| Heading 1 | Heading 2 |
|:----------|:----------|
|Cell 1     | Cell 2    |
|Cell 3     | Cell 4    |

- List item 1
- List item 2
- List item 3

1. List item 1
2. List item 2
3. List item 3

* List item 1
* List item 2
* List item 3

:::note
  This is a note admonition
:::

:::tip
  This is a tip admonition
:::

:::info
  This is a info admonition
:::

:::caution
  This is a caution admonition
:::

:::warning
  This is a warning admonition
:::

:::danger
  This is a danger admonition
:::

`;

export const Primary = Template.bind({});
Primary.args = {
  content,
};
