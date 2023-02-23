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

export const ConditionLabel = Template.bind({});
ConditionLabel.args = {
  // a "form field" from the useBuildForm() hook
  property: {
    isRequired: false,
    _type: "formCondition",
    fieldKey: "field_key",
    path: "section.Fieldname",
    selectionKey: "type",
    selectionPath: "section.Fieldname.type",
    selectionConstValues: ["one", "two", "three"],
    conditions: [
      {
        isRequired: true,
        _type: "formGroup",
        properties: [],
        fieldKey: "field_key",
        path: "section.Fieldname",
        title: "Title of first option",
        description: "Description of the item",
      },
      {
        isRequired: true,
        _type: "formGroup",
        properties: [],
        fieldKey: "field_key",
        path: "section.Fieldname",
      },
      {
        isRequired: true,
        _type: "formGroup",
        properties: [],
        fieldKey: "field_key",
        path: "section.Fieldname",
        description:
          "Sometimes the description can be a bit longer - in this case there is a lot of text in here and so on.",
      },
    ],
  },
  label: "Property name",
  description: "The description of the property, placed in the info tooltip",
  children: <Input type="text" />,
};
