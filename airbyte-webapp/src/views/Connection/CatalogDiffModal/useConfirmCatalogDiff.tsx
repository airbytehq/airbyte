import { useEffect } from "react";
import { useIntl } from "react-intl";

import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useModalService } from "hooks/services/Modal";

import { CatalogDiffModal } from "./CatalogDiffModal";

export const useConfirmCatalogDiff = () => {
  const { formatMessage } = useIntl();
  const { openModal } = useModalService();
  const { connection } = useConnectionEditService();

  useEffect(() => {
    // If we have a catalogDiff we always want to show the modal
    const { catalogDiff, syncCatalog } = connection;
    if (catalogDiff?.transforms && catalogDiff.transforms?.length > 0) {
      openModal<void>({
        title: formatMessage({ id: "connection.updateSchema.completed" }),
        preventCancel: true,
        size: "md",
        content: ({ onClose }) => (
          <CatalogDiffModal catalogDiff={catalogDiff} catalog={syncCatalog} onClose={onClose} />
        ),
      });
    }
  }, [connection, formatMessage, openModal]);
};
