import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useAsyncFn } from "react-use";

import { ControlLabels } from "components";
import { Card } from "components/ui/Card";
import { Switch } from "components/ui/Switch";
import { ToastType } from "components/ui/Toast";

import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useNotificationService } from "hooks/services/Notification";

import styles from "./SchemaUpdateNotifications.module.scss";

export const SchemaUpdateNotifications: React.FC = () => {
  const { formatMessage } = useIntl();
  const { registerNotification } = useNotificationService();
  const { connection, updateConnection, connectionUpdating } = useConnectionEditService();
  const [{ loading }, onChange] = useAsyncFn(async (checked: boolean) => {
    try {
      await updateConnection({
        connectionId: connection.connectionId,
        notifySchemaChanges: checked,
      });
    } catch (e) {
      registerNotification({
        id: "connection.schemaUpdateNotifications.error",
        text: formatMessage({ id: "connection.schemaUpdateNotifications.error" }),
        type: ToastType.ERROR,
      });
    }
  });

  return (
    <Card withPadding className={styles.container}>
      <ControlLabels
        nextLine
        label={<FormattedMessage id="connection.schemaUpdateNotifications.title" />}
        message={<FormattedMessage id="connection.schemaUpdateNotifications.info" />}
      />
      <Switch
        checked={connection.notifySchemaChanges}
        onChange={(event) => onChange(event.target.checked)}
        disabled={connectionUpdating}
        loading={loading}
      />
    </Card>
  );
};
