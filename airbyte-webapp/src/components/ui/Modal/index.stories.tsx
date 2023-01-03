import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Button } from "components/ui/Button";

import { Modal, ModalBody, ModalFooter } from ".";

export default {
  title: "UI/Modal",
  component: Modal,
  argTypes: {
    title: { type: { name: "string", required: false } },
  },
} as ComponentMeta<typeof Modal>;

const Template: ComponentStory<typeof Modal> = (args) => {
  if (args.cardless) {
    return <Modal {...args} />;
  }

  return (
    <Modal {...args}>
      <ModalBody>{args.children}</ModalBody>
      <ModalFooter>
        <Button>Lorem</Button>
        <Button>Ipsum</Button>
      </ModalFooter>
    </Modal>
  );
};

export const Primary = Template.bind({});
Primary.args = {
  size: "md",
  children: (
    <div>
      <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
        magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat.
      </p>
      <p>
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur
        sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      </p>
    </div>
  ),
  title: "Modal Title",
};
