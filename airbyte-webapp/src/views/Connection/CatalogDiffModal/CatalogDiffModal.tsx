import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components";

import { AirbyteCatalog, CatalogDiff } from "core/request/AirbyteClient";

import { ModalBody, ModalFooter } from "../../../components/Modal";
import styles from "./CatalogDiffModal.module.scss";
import { DiffSection } from "./components/DiffSection";
import { FieldSection } from "./components/FieldSection";
import { getSortedDiff } from "./utils";

interface CatalogDiffModalProps {
  catalogDiff: CatalogDiff;
  catalog: AirbyteCatalog;
  onClose: () => void;
}

export const CatalogDiffModal: React.FC<CatalogDiffModalProps> = ({ catalogDiff, catalog, onClose }) => {
  const { newItems, removedItems, changedItems } = useMemo(
    () => getSortedDiff(catalogDiff.transforms),
    [catalogDiff.transforms]
  );

  return (
    <>
      <ModalBody maxHeight={400} padded={false}>
        <div className={styles.modalContent}>
          {removedItems.length > 0 && <DiffSection streams={removedItems} diffVerb="removed" catalog={catalog} />}
          {newItems.length > 0 && <DiffSection streams={newItems} diffVerb="new" />}
          {changedItems.length > 0 && <FieldSection streams={changedItems} diffVerb="changed" />}
        </div>
      </ModalBody>
      <ModalFooter>
        <Button onClick={() => onClose()}>
          <FormattedMessage id="connection.updateSchema.confirm" />
        </Button>
      </ModalFooter>
    </>
  );
};
