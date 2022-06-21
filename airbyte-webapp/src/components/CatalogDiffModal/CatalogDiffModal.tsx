import { FormattedMessage } from "react-intl";

import { AirbyteCatalog, CatalogDiff } from "core/request/AirbyteClient";

import { Modal } from "../Modal";
import { CatalogDiffModalSection } from "./components/CatalogDiffModalSection";

interface CatalogDiffModalProps {
  catalogDiff: CatalogDiff;
  catalog: AirbyteCatalog;
}

export const CatalogDiffModal: React.FC<CatalogDiffModalProps> = ({ catalogDiff, catalog }) => {
  const addedStreams = catalogDiff.transforms.filter((item) => item.transformType === "add_stream");
  const removedStreams = catalogDiff.transforms.filter((item) => item.transformType === "remove_stream");

  const updatedStreams = catalogDiff.transforms.filter((item) => item.transformType === "update_stream");

  return (
    <>
      <Modal title={<FormattedMessage id="connection.updateSchema.completed" />}>
        {addedStreams.length > 1 && <CatalogDiffModalSection data={addedStreams} catalog={catalog} />}
        {removedStreams.length > 1 && <CatalogDiffModalSection data={removedStreams} catalog={catalog} />}
        {updatedStreams.length > 1 && <CatalogDiffModalSection data={updatedStreams} catalog={catalog} />}
      </Modal>
    </>
  );
};
