import { ComponentStory, ComponentMeta } from "@storybook/react";
import { FormattedMessage } from "react-intl";

import Modal from "components/Modal";

import { CatalogDiffModal } from "./CatalogDiffModal";

export default {
  title: "Ui/CatalogDiffModal",
  component: CatalogDiffModal,
} as ComponentMeta<typeof CatalogDiffModal>;

const Template: ComponentStory<typeof CatalogDiffModal> = (args) => {
  return (
    <Modal title={<FormattedMessage id="connection.updateSchema.completed" />}>
      <CatalogDiffModal
        catalogDiff={args.catalogDiff}
        catalog={args.catalog}
        onClose={() => {
          return null;
        }}
      />
    </Modal>
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
          { transformType: "add_field", fieldName: ["users", "phone"] },
          { transformType: "add_field", fieldName: ["users", "email"] },
          { transformType: "remove_field", fieldName: ["users", "lastName"] },

          {
            transformType: "update_field_schema",
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
