import { Dispatch, SetStateAction } from "react";
import { FormattedMessage } from "react-intl";

import { LoadingButton } from "components";

import { AirbyteCatalog, CatalogDiff } from "core/request/AirbyteClient";

import { Modal } from "../../../components/Modal";
import { CatalogProvider, useCatalogContext } from "./CatalogContext";
import styles from "./CatalogDiffModal.module.scss";
import { DiffSection } from "./components/DiffSection";

interface CatalogDiffModalProps {
  catalogDiff: CatalogDiff;
  catalog: AirbyteCatalog;
  setDiffAcknowledged: Dispatch<SetStateAction<boolean>>;
}
export const CatalogDiffModal: React.FC<CatalogDiffModalProps> = ({ catalogDiff, catalog, setDiffAcknowledged }) => {
  const { setCatalog } = useCatalogContext();
  setCatalog(catalog);

  // const addedStreams = catalogDiff.transforms.filter((item) => item.transformType === "add_stream");
  // const removedStreams = catalogDiff.transforms.filter((item) => item.transformType === "remove_stream");
  // const updatedStreams = catalogDiff.transforms.filter((item) => item.transformType === "update_stream");

  //todo: remove this and uncomment above for review... this is just to force the modal regardless of your source schema during dev
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
        <CatalogProvider>
          {removedStreams.length > 0 && <DiffSection streams={removedStreams} />}
          {addedStreams.length > 0 && <DiffSection streams={addedStreams} />}
          {updatedStreams.length > 0 && <DiffSection streams={updatedStreams} />}
        </CatalogProvider>
      </div>
      <div className={styles.buttonContainer}>
        <LoadingButton onClick={() => setDiffAcknowledged(true)}>
          <FormattedMessage id="connection.updateSchema.confirm" />
        </LoadingButton>
      </div>
    </Modal>
  );
};
