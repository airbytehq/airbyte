import { faChevronDown, faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Disclosure } from "@headlessui/react";
import React from "react";
import { FormattedMessage } from "react-intl";
import { Navigate } from "react-router-dom";

import { DeleteBlock } from "components/common/DeleteBlock";
import { UpdateConnectionDataResidency } from "components/connection/UpdateConnectionDataResidency";
import { Button } from "components/ui/Button";
import { Spinner } from "components/ui/Spinner";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useDeleteConnection } from "hooks/services/useConnectionHook";

import styles from "./ConnectionSettingsPage.module.scss";
import { SchemaUpdateNotifications } from "./SchemaUpdateNotifications";
import { StateBlock } from "./StateBlock";

export const ConnectionSettingsPageInner: React.FC = () => {
  const { connection } = useConnectionEditService();
  const { mutateAsync: deleteConnection } = useDeleteConnection();
  const canUpdateDataResidency = useFeature(FeatureItem.AllowChangeDataGeographies);
  // TODO: Disabled until feature is implemented in backend
  const canSendSchemaUpdateNotifications = false; // useFeature(FeatureItem.AllowAutoDetectSchema);

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_SETTINGS);
  const onDelete = () => deleteConnection(connection);

  return (
    <div className={styles.container}>
      {canSendSchemaUpdateNotifications && <SchemaUpdateNotifications />}
      {canUpdateDataResidency && <UpdateConnectionDataResidency />}
      <DeleteBlock type="connection" onDelete={onDelete} />
      <Disclosure>
        {({ open }) => (
          <>
            <Disclosure.Button
              as={Button}
              variant="clear"
              icon={<FontAwesomeIcon icon={open ? faChevronDown : faChevronRight} />}
              className={styles.advancedButton}
            >
              <FormattedMessage id="connectionForm.settings.advancedButton" />
            </Disclosure.Button>
            <Disclosure.Panel className={styles.advancedPanel}>
              <React.Suspense fallback={<Spinner />}>
                <StateBlock connectionId={connection.connectionId} />
              </React.Suspense>
            </Disclosure.Panel>
          </>
        )}
      </Disclosure>
    </div>
  );
};

export const ConnectionSettingsPage: React.FC = () => {
  const { connection } = useConnectionEditService();
  const isConnectionDeleted = connection.status === ConnectionStatus.deprecated;

  return isConnectionDeleted ? <Navigate replace to=".." /> : <ConnectionSettingsPageInner />;
};
