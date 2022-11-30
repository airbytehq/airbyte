import { ComponentStory, ComponentMeta } from "@storybook/react";
import { FormattedMessage } from "react-intl";

import { Modal } from "components/ui/Modal";

import { CatalogDiff } from "core/request/AirbyteClient";
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
        <CatalogDiffModal catalogDiff={args.catalogDiff} catalog={args.catalog} onClose={() => null} />
      </Modal>
    </ModalServiceProvider>
  );
};

const oneStreamAddCatalogDiff: CatalogDiff = {
  transforms: [
    {
      transformType: "add_stream",
      streamDescriptor: { namespace: "apple", name: "banana" },
    },
  ],
};

const oneFieldAddCatalogDiff: CatalogDiff = {
  transforms: [
    {
      transformType: "update_stream",
      streamDescriptor: { namespace: "apple", name: "harissa_paste" },
      updateStream: [{ transformType: "add_field", fieldName: ["users", "phone"], breaking: false }],
    },
  ],
};

const oneFieldUpdateCatalogDiff: CatalogDiff = {
  transforms: [
    {
      transformType: "update_stream",
      streamDescriptor: { namespace: "apple", name: "harissa_paste" },
      updateStream: [
        {
          transformType: "update_field_schema",
          breaking: false,
          fieldName: ["users", "address"],
          updateFieldSchema: { oldSchema: { type: "number" }, newSchema: { type: "string" } },
        },
      ],
    },
  ],
};

const fullCatalogDiff: CatalogDiff = {
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
        {
          transformType: "update_field_schema",
          breaking: false,
          fieldName: ["users", "updated_at"],
          updateFieldSchema: { oldSchema: { type: "string" }, newSchema: { type: "DateTime" } },
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
};

export const Primary = Template.bind({});
Primary.args = {
  catalogDiff: fullCatalogDiff,
  catalog: { streams: [] },
};

export const OneStreamAdd = Template.bind({});
OneStreamAdd.args = {
  catalogDiff: oneStreamAddCatalogDiff,
  catalog: { streams: [] },
};

export const OneFieldAdd = Template.bind({});
OneFieldAdd.args = {
  catalogDiff: oneFieldAddCatalogDiff,
  catalog: { streams: [] },
};

export const OneFieldUpdate = Template.bind({});
OneFieldUpdate.args = {
  catalogDiff: oneFieldUpdateCatalogDiff,
  catalog: { streams: [] },
};
