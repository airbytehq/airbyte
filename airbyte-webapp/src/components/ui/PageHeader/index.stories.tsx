import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { ComponentStory, ComponentMeta } from "@storybook/react";

import { PageHeader } from "./PageHeader";
import { Button } from "../Button";

export default {
  title: "UI/PageHeader",
  component: PageHeader,
  argTypes: {},
} as ComponentMeta<typeof PageHeader>;

const Template: ComponentStory<typeof PageHeader> = (args) => <PageHeader {...args} />;

const title = "Connections";

const endComponent = (
  <Button icon={<FontAwesomeIcon icon={faPlus} />} variant="primary" size="sm">
    New Source
  </Button>
);

export const Primary = Template.bind({});
Primary.args = {
  title,
  endComponent,
};
