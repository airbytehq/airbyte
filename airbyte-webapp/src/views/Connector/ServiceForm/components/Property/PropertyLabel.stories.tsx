import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Card } from "components/ui/Card";
import { Input } from "components/ui/Input";

import { PropertyLabel } from "./PropertyLabel";

export default {
  title: "Connector/PropertyLabel",
  component: PropertyLabel,
} as ComponentMeta<typeof PropertyLabel>;

const Template: ComponentStory<typeof PropertyLabel> = (args) => (
  <Card withPadding>
    <PropertyLabel {...args} />
  </Card>
);

export const Primary = Template.bind({});
Primary.args = {
  // a "form field" from the useBuildForm() hook
  property: {
    isRequired: true,
    type: "string",
    _type: "formItem",
    fieldKey: "field_key",
    path: "section.Fieldname",
    examples: ["First example", "Second example"],
  },
  label: "Property name",
  description: "The description of the property, placed in the info tooltip",
  // overrides the property.isRequired value if set
  optional: true,
  children: <Input type="text" />,
};
