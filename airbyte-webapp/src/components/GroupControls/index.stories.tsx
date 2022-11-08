import { ComponentStory, ComponentMeta } from "@storybook/react";

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
  conditions: {
    ChoiceOne: {
      isRequired: true,
      _type: "formGroup",
      fieldKey: "choice_one_key",
      path: "section.conditional.choice_one",
      jsonSchema: {},
      properties: [propOneFormBlock, propTwoFormBlock],
    },
  },
  isRequired: true,
  _type: "formCondition",
  fieldKey: "field_key",
  path: "section.conditional",
};

const title = <GroupLabel formField={conditionFormField} />;

export const Empty = Template.bind({});
Empty.args = {
  title,
};

export const WithContent = Template.bind({});
WithContent.args = {
  title,
  children: (
    <>
      <SectionContainer>Content part 1</SectionContainer>
      <SectionContainer>Content part 2</SectionContainer>
    </>
  ),
};
