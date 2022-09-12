import { ComponentStory, ComponentMeta } from "@storybook/react";

import { GroupLabel } from "views/Connector/ServiceForm/components/Sections/GroupLabel";

import GroupControls from "./GroupControls";

export default {
  title: "Composed/GroupControls",
  component: GroupControls,
} as ComponentMeta<typeof GroupControls>;

const Template: ComponentStory<typeof GroupControls> = (args) => <GroupControls {...args} />;

const title = (
  <GroupLabel
    formField={{
      conditions: {
        ChoiceOne: {
          isRequired: true,
          _type: "formGroup",
          fieldKey: "choice_one_key",
          path: "section.conditional.choice_one",
          jsonSchema: {},
          properties: [
            {
              title: "propOne",
              type: "string",
              isRequired: true,
              _type: "formItem",
              fieldKey: "propOneKey",
              path: "section.conditional.choice_one.prop_one",
            },
          ],
        },
      },
      isRequired: true,
      _type: "formCondition",
      fieldKey: "field_key",
      path: "section.conditional",
    }}
  />
);

export const Empty = Template.bind({});
Empty.args = {
  title,
};

export const WithContent = Template.bind({});
WithContent.args = {
  title,
  children: (
    <>
      <p>Content part 1</p>
      <p>Content part 2</p>
    </>
  ),
};
