import { ComponentStory, ComponentMeta } from "@storybook/react";
import { FormattedMessage } from "react-intl";

import { Modal } from "components/ui/Modal";

import { ModalServiceProvider } from "hooks/services/Modal";

import { CatalogDiffModal } from "./CatalogDiffModal";

export default {
  title: "connection/CatalogDiffModal",
  component: CatalogDiffModal,
} as ComponentMeta<typeof CatalogDiffModal>;

const Template: ComponentStory<typeof CatalogDiffModal> = (args) => {
  return (
    <ModalServiceProvider>
      <Modal size="md" title={<FormattedMessage id="connection.updateSchema.completed" />}>
        <CatalogDiffModal
          catalogDiff={args.catalogDiff}
          catalog={args.catalog}
          onClose={() => {
            return null;
          }}
        />
      </Modal>
    </ModalServiceProvider>
  );
};

export const Primary = Template.bind({});

Primary.args = {
  catalogDiff: {
    transforms: [
      {
        transformType: "update_stream",
        streamDescriptor: { namespace: "apple", name: "harissa_paste" },
        updateStream: [
          { transformType: "add_field", fieldName: ["users", "phone"], breaking: false },
          { transformType: "add_field", fieldName: ["users", "email"], breaking: false },
          { transformType: "remove_field", fieldName: ["users", "lastName"], breaking: false },

          {
            transformType: "update_field_schema",
            breaking: false,
            fieldName: ["users", "address"],
            updateFieldSchema: { oldSchema: { type: "number" }, newSchema: { type: "string" } },
          },
        ],
      },
      {
        transformType: "add_stream",
        streamDescriptor: { namespace: "apple", name: "banana" },
      },
      {
        transformType: "add_stream",
        streamDescriptor: { namespace: "apple", name: "carrot" },
      },
      {
        transformType: "remove_stream",
        streamDescriptor: { namespace: "apple", name: "dragonfruit" },
      },
      {
        transformType: "remove_stream",
        streamDescriptor: { namespace: "apple", name: "eclair" },
      },
      {
        transformType: "remove_stream",
        streamDescriptor: { namespace: "apple", name: "fishcake" },
      },
      {
        transformType: "remove_stream",
        streamDescriptor: { namespace: "apple", name: "gelatin_mold" },
      },
    ],
  },
  catalog: { streams: [] },
};
