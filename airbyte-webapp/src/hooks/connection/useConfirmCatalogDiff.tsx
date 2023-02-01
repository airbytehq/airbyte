import { useEffect } from "react";
import { useIntl } from "react-intl";

import { CatalogDiffModal } from "components/connection/CatalogDiffModal/CatalogDiffModal";

import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useModalService } from "hooks/services/Modal";

export const useConfirmCatalogDiff = () => {
  const { formatMessage } = useIntl();
  const { openModal } = useModalService();
  const { connection } = useConnectionEditService();
  const { catalogDiff, syncCatalog } = connection;

  useEffect(() => {
    // If we have a catalogDiff we always want to show the modal
    if (catalogDiff?.transforms && catalogDiff.transforms?.length > 0) {
      openModal<void>({
        title: formatMessage({ id: "connection.updateSchema.completed" }),
        preventCancel: true,
        size: "md",
        testId: "catalog-diff-modal",
        content: ({ onClose }) => (
          <CatalogDiffModal catalogDiff={catalogDiff} catalog={syncCatalog} onClose={onClose} />
        ),
      });
    }
  }, [catalogDiff, syncCatalog, formatMessage, openModal]);
};
