import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Text } from "components/ui/Text";

import { ExternalLink } from "./index";

export default {
  title: "Ui/ExternalLink",
  component: ExternalLink,
} as ComponentMeta<typeof ExternalLink>;

const Template: ComponentStory<typeof ExternalLink> = (args) => <ExternalLink {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  children: "External link",
  href: "https://airbyte.com",
  opensInNewTab: true,
};

export const WithinText = () => (
  <>
    <Text size="lg">
      Large sized text <ExternalLink href="https://docs.airbyte.com">Learn more</ExternalLink>.
    </Text>
    <Text size="sm">
      Small sized text <ExternalLink href="https://docs.airbyte.com">Learn more</ExternalLink>.
    </Text>
  </>
);
