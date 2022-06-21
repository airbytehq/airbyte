import { FormattedMessage } from "react-intl";

import { AirbyteCatalog, CatalogDiff } from "core/request/AirbyteClient";

import { Modal } from "../../../components/Modal";
import { CatalogDiffAccordion } from "./components/CatalogDiffAccordion";
import { CatalogDiffSection } from "./components/CatalogDiffSection";

interface CatalogDiffModalProps {
  catalogDiff: CatalogDiff;
  catalog: AirbyteCatalog;
}

export const CatalogDiffModal: React.FC<CatalogDiffModalProps> = ({ catalogDiff, catalog }) => {
  const addedStreams = catalogDiff.transforms.filter((item) => item.transformType === "add_stream");
  const removedStreams = catalogDiff.transforms.filter((item) => item.transformType === "remove_stream");
  const updatedStreams = catalogDiff.transforms.filter((item) => item.transformType === "update_stream");

  return (
    <Modal title={<FormattedMessage id="connection.updateSchema.completed" />}>
      {addedStreams.length > 1 && <CatalogDiffSection data={addedStreams} catalog={catalog} />}
      {removedStreams.length > 1 && <CatalogDiffSection data={removedStreams} catalog={catalog} />}
      {updatedStreams.length > 1 && <CatalogDiffAccordion data={updatedStreams} catalog={catalog} />}
    </Modal>
  );
};
