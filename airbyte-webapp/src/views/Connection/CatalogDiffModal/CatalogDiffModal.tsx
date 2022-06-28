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
  const addedStreams = catalogDiff.transforms.filter((item) => item.transformType === "add_stream");
  const removedStreams = catalogDiff.transforms.filter((item) => item.transformType === "remove_stream");
  const updatedStreams = catalogDiff.transforms.filter((item) => item.transformType === "update_stream");

  return (
    <Modal title={<FormattedMessage id="connection.updateSchema.completed" />} onClose={() => null}>
      <div className={styles.modalContent}>
        {addedStreams.length > 1 && <CatalogDiffSection data={addedStreams} catalog={catalog} />}
        {removedStreams.length > 1 && <CatalogDiffSection data={removedStreams} catalog={catalog} />}
        {updatedStreams.length > 1 && <CatalogDiffSection data={updatedStreams} catalog={catalog} />}
      </div>
      <LoadingButton onClick={() => setDiffAcknowledged(true)}>
        <FormattedMessage id="connection.updateSchema.confirm" />
      </LoadingButton>
    </Modal>
  );
};
