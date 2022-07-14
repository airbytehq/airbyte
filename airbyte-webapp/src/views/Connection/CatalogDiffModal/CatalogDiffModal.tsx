import { Dispatch, SetStateAction } from "react";
import { FormattedMessage } from "react-intl";

import { LoadingButton } from "components";

import { AirbyteCatalog, CatalogDiff, FieldTransform, StreamTransform } from "core/request/AirbyteClient";

import { Modal } from "../../../components/Modal";
import styles from "./CatalogDiffModal.module.scss";
import { DiffSection } from "./components/DiffSection";
import { FieldSection } from "./components/FieldSection";

interface CatalogDiffModalProps {
  catalogDiff: CatalogDiff;
  catalog: AirbyteCatalog;
  setDiffAcknowledged: Dispatch<SetStateAction<boolean>>;
}

export type DiffVerb = "new" | "removed" | "changed";

interface SortedDiff<T extends StreamTransform | FieldTransform> {
  newItems: T[];
  removedItems: T[];
  changedItems: T[];
}

export const diffReducer = <T extends StreamTransform | FieldTransform>(diffArray: T[]): SortedDiff<T> => {
  const sortedDiff: SortedDiff<T> = { newItems: [], removedItems: [], changedItems: [] };

  diffArray.filter((streamTransform) => {
    if (streamTransform.transformType.includes("add")) {
      sortedDiff.newItems.push(streamTransform);
    }

    if (streamTransform.transformType.includes("remove")) {
      sortedDiff.removedItems.push(streamTransform);
    }

    if (streamTransform.transformType.includes("update")) {
      sortedDiff.changedItems.push(streamTransform);
    }
    return sortedDiff;
  });
  return sortedDiff;
};
export const CatalogDiffModal: React.FC<CatalogDiffModalProps> = ({ catalogDiff, catalog, setDiffAcknowledged }) => {
  const { newItems, removedItems, changedItems } = diffReducer(catalogDiff.transforms);

  return (
    <Modal title={<FormattedMessage id="connection.updateSchema.completed" />} onClose={() => null}>
      <div className={styles.modalContent}>
        {removedItems.length > 0 && <DiffSection streams={removedItems} diffVerb="removed" catalog={catalog} />}
        {newItems.length > 0 && <DiffSection streams={newItems} diffVerb="new" />}
        {changedItems.length > 0 && <FieldSection streams={changedItems} diffVerb="changed" />}
      </div>
      <div className={styles.buttonContainer}>
        <LoadingButton onClick={() => setDiffAcknowledged(true)}>
          <FormattedMessage id="connection.updateSchema.confirm" />
        </LoadingButton>
      </div>
    </Modal>
  );
};
