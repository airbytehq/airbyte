import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Modal, ModalBody, ModalFooter } from "./";

export default {
  title: "Ui/Modal",
  component: Modal,
  argTypes: {
    title: { type: { name: "string", required: false } },
  },
} as ComponentMeta<typeof Modal>;

const Template: ComponentStory<typeof Modal> = (args) => {
  if (args.clear) {
    return <Modal {...args} />;
  }

  return (
    <Modal {...args}>
      <ModalBody>{args.children}</ModalBody>
      <ModalFooter>
        <button>Button 1</button>
        <button>Button 2</button>
      </ModalFooter>
    </Modal>
  );
};

export const Primary = Template.bind({});
Primary.args = {
  children: "Modal children go here.",
  title: "Modal Title",
};
