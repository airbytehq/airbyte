import { FieldProps } from "formik";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";

import { CatalogTree } from "components/connection/CatalogTree";
import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";

import { SyncSchemaStream } from "core/domain/catalog";
import { DestinationSyncMode } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import styles from "./SyncCatalogField.module.scss";

interface SchemaViewProps extends FieldProps<SyncSchemaStream[]> {
  additionalControl?: React.ReactNode;
  destinationSupportedSyncModes: DestinationSyncMode[];
  isSubmitting: boolean;
}

const SyncCatalogFieldComponent: React.FC<React.PropsWithChildren<SchemaViewProps>> = ({
  additionalControl,
  field,
  form,
  isSubmitting,
}) => {
  const { mode } = useConnectionFormService();

  const { value: streams, name: fieldName } = field;

  const setField = form.setFieldValue;

  const onStreamsUpdated = useCallback(
    (newValue: SyncSchemaStream[]) => {
      setField(fieldName, newValue);
    },
    [fieldName, setField]
  );

  return (
    <>
      <div className={styles.header}>
        <Heading as="h2" size="sm">
          <FormattedMessage id={mode === "readonly" ? "form.dataSync.readonly" : "form.dataSync"} />
        </Heading>
        <div className={styles.actions}>
          <Button type="button" variant="clear" className={styles.feedback}>
            <a href="https://forms.gle/5wDQHf6hL5sCvLgK7" target="_blank" rel="noreferrer">
              <FormattedMessage id="form.leaveFeedback" />
            </a>
          </Button>
          {mode !== "readonly" && additionalControl}
        </div>
      </div>
      <CatalogTree streams={streams} onStreamsChanged={onStreamsUpdated} isLoading={isSubmitting} />
    </>
  );
};

export const SyncCatalogField = React.memo(SyncCatalogFieldComponent);
