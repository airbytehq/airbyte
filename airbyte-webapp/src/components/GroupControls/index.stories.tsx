import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";

import { FormBlock, FormConditionItem } from "core/form/types";
import { GroupLabel } from "views/Connector/ConnectorForm/components/Sections/GroupLabel";
import { SectionContainer } from "views/Connector/ConnectorForm/components/Sections/SectionContainer";

import GroupControls from "./GroupControls";

export default {
  title: "UI/GroupControls",
  component: GroupControls,
} as ComponentMeta<typeof GroupControls>;

const Template: ComponentStory<typeof GroupControls> = (args) => (
  <Card withPadding>
    <GroupControls {...args} />
  </Card>
);

const propOneFormBlock: FormBlock = {
  title: "propOne",
  type: "string",
  isRequired: true,
  _type: "formItem",
  fieldKey: "propOneKey",
  path: "section.conditional.choice_one.prop_one",
};

const propTwoFormBlock: FormBlock = {
  title: "propTwo",
  type: "string",
  isRequired: false,
  _type: "formItem",
  fieldKey: "propTwoKey",
  path: "section.conditional.choice_one.prop_two",
};

const conditionFormField: FormConditionItem = {
  conditions: [
    {
      isRequired: true,
      _type: "formGroup",
      fieldKey: "choice_one_key",
      path: "section.conditional.choice_one",
      properties: [propOneFormBlock, propTwoFormBlock],
    },
  ],
  selectionPath: "section.conditional.choice_one.type",
  selectionKey: "type",
  selectionConstValues: ["one"],
  isRequired: true,
  _type: "formCondition",
  fieldKey: "field_key",
  path: "section.conditional",
};

const label = <GroupLabel formField={conditionFormField} />;

export const Empty = Template.bind({});
Empty.args = {
  label,
};

export const WithContent = Template.bind({});
WithContent.args = {
  label,
  children: (
    <>
      <SectionContainer>Content part 1</SectionContainer>
      <SectionContainer>Content part 2</SectionContainer>
    </>
  ),
};

export const EmptyWithControl = Template.bind({});
EmptyWithControl.args = {
  label,
  control: <Button variant="secondary">Control</Button>,
};

export const ControlAndContent = Template.bind({});
ControlAndContent.args = {
  label,
  control: <Button variant="secondary">Control</Button>,
  children: (
    <>
      <SectionContainer>Content part 1</SectionContainer>
      <SectionContainer>Content part 2</SectionContainer>
    </>
  ),
};
