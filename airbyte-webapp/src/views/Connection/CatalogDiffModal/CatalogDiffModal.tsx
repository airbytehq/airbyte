import { Dispatch, SetStateAction } from "react";
import { FormattedMessage } from "react-intl";

import { LoadingButton } from "components";

import { AirbyteCatalog, CatalogDiff } from "core/request/AirbyteClient";

import { Modal } from "../../../components/Modal";
import styles from "./CatalogDiffModal.module.scss";
import { CatalogDiffSection } from "./components/CatalogDiffSection";

interface CatalogDiffModalProps {
  catalogDiff: CatalogDiff;
  catalog: AirbyteCatalog;
  setDiffAcknowledged: Dispatch<SetStateAction<boolean>>;
}
export const CatalogDiffModal: React.FC<CatalogDiffModalProps> = ({ catalogDiff, catalog, setDiffAcknowledged }) => {
  let addedStreams = catalogDiff.transforms.filter((item) => item.transformType === "add_stream");
  let removedStreams = catalogDiff.transforms.filter((item) => item.transformType === "remove_stream");
  let updatedStreams = catalogDiff.transforms.filter((item) => item.transformType === "update_stream");

  if (!addedStreams.length) {
    addedStreams = [
      {
        transformType: "add_stream",
        streamDescriptor: { namespace: "apple", name: "banana" },
      },
      {
        transformType: "add_stream",
        streamDescriptor: { namespace: "apple", name: "carrot" },
      },
    ];
  }
  if (!removedStreams.length) {
    removedStreams = [
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
    ];
  }
  if (!updatedStreams.length) {
    updatedStreams = [
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
    ];
  }

  return (
    <Modal title={<FormattedMessage id="connection.updateSchema.completed" />} onClose={() => null}>
      <div className={styles.modalContent}>
        {removedStreams.length > 0 && <CatalogDiffSection data={removedStreams} catalog={catalog} />}
        {addedStreams.length > 0 && <CatalogDiffSection data={addedStreams} catalog={catalog} />}
        {updatedStreams.length > 0 && <CatalogDiffSection data={updatedStreams} catalog={catalog} />}
      </div>
      <div className={styles.buttonContainer}>
        <LoadingButton onClick={() => setDiffAcknowledged(true)}>
          <FormattedMessage id="connection.updateSchema.confirm" />
        </LoadingButton>
      </div>
    </Modal>
  );
};
