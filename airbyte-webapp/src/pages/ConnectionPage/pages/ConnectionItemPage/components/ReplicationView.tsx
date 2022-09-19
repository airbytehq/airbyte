import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useAsyncFn, useUnmount } from "react-use";
import styled from "styled-components";

import { Button, LabeledSwitch, ModalBody, ModalFooter } from "components";
import LoadingSchema from "components/LoadingSchema";

import { toWebBackendConnectionUpdate } from "core/domain/connection";
import { ConnectionStateType, ConnectionStatus } from "core/request/AirbyteClient";
import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { ConnectionFormServiceProvider } from "hooks/services/Connection/ConnectionFormService";
import { useChangedFormsById, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { ModalCancel, useModalService } from "hooks/services/Modal";
import {
  useConnectionLoad,
  useConnectionService,
  useUpdateConnection,
  ValuesProps,
} from "hooks/services/useConnectionHook";
import { equal, naturalComparatorBy } from "utils/objects";
import { CatalogDiffModal } from "views/Connection/CatalogDiffModal/CatalogDiffModal";
import { ConnectionForm } from "views/Connection/ConnectionForm";

interface ReplicationViewProps {
  onAfterSaveSchema: () => void;
  connectionId: string;
}

interface ResetWarningModalProps {
  onClose: (withReset: boolean) => void;
  onCancel: () => void;
  stateType: ConnectionStateType;
}

const ResetWarningModal: React.FC<ResetWarningModalProps> = ({ onCancel, onClose, stateType }) => {
  const { formatMessage } = useIntl();
  const [withReset, setWithReset] = useState(true);
  const requireFullReset = stateType === ConnectionStateType.legacy;
  return (
    <>
      <ModalBody>
        {/* 
        TODO: This should use proper text stylings once we have them available.
        See https://github.com/airbytehq/airbyte/issues/14478
      */}
        <FormattedMessage id={requireFullReset ? "connection.streamFullResetHint" : "connection.streamResetHint"} />
        <p>
          <LabeledSwitch
            checked={withReset}
            onChange={(ev) => setWithReset(ev.target.checked)}
            label={formatMessage({
              id: requireFullReset ? "connection.saveWithFullReset" : "connection.saveWithReset",
            })}
            checkbox
            data-testid="resetModal-reset-checkbox"
          />
        </p>
      </ModalBody>
      <ModalFooter>
        <Button onClick={onCancel} secondary data-testid="resetModal-cancel">
          <FormattedMessage id="form.cancel" />
        </Button>
        <Button onClick={() => onClose(withReset)} data-testid="resetModal-save">
          <FormattedMessage id="connection.save" />
        </Button>
      </ModalFooter>
    </>
  );
};

const Content = styled.div`
  max-width: 1279px;
  margin: 0 auto;
  padding-bottom: 10px;
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin: 0 10px -1px 0;
  font-size: 14px;
`;

export const ReplicationView: React.FC<ReplicationViewProps> = ({ onAfterSaveSchema, connectionId }) => {
  const { formatMessage } = useIntl();
  const { openModal, closeModal } = useModalService();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const [activeUpdatingSchemaMode, setActiveUpdatingSchemaMode] = useState(false);
  const [saved, setSaved] = useState(false);
  const connectionService = useConnectionService();
  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_REPLICATION);

  const { mutateAsync: updateConnection } = useUpdateConnection();

  const { connection: initialConnection, refreshConnectionCatalog } = useConnectionLoad(connectionId);

  const [{ value: connectionWithRefreshCatalog, loading: isRefreshingCatalog }, refreshCatalog] = useAsyncFn(
    refreshConnectionCatalog,
    [connectionId]
  );

  const formId = useUniqueFormId();

  const [changedFormsById] = useChangedFormsById();
  const formDirty = useMemo(() => !!changedFormsById?.[formId], [changedFormsById, formId]);

  useUnmount(() => {
    closeModal();
    closeConfirmationModal();
  });

  const connection = activeUpdatingSchemaMode ? connectionWithRefreshCatalog : initialConnection;

  const saveConnection = async (values: ValuesProps, { skipReset }: { skipReset: boolean }) => {
    if (!connection) {
      // onSubmit should only be called while the catalog isn't currently refreshing at the moment,
      // which is the only case when `connection` would be `undefined`.
      return;
    }
    const initialSyncSchema = connection.syncCatalog;
    const connectionAsUpdate = toWebBackendConnectionUpdate(connection);

    await updateConnection({
      ...connectionAsUpdate,
      ...values,
      connectionId,
      // Use the name and status from the initial connection because
      // The status can be toggled and the name can be changed in-between refreshing the schema
      name: initialConnection.name,
      status: initialConnection.status || "",
      skipReset,
    });

    setSaved(true);
    if (!equal(values.syncCatalog, initialSyncSchema)) {
      onAfterSaveSchema();
    }

    if (activeUpdatingSchemaMode) {
      setActiveUpdatingSchemaMode(false);
    }
  };

  const onSubmitForm = async (values: ValuesProps): Promise<void> => {
    // Detect whether the catalog has any differences in its enabled streams compared to the original one.
    // This could be due to user changes (e.g. in the sync mode) or due to new/removed
    // streams due to a "refreshed source schema".
    const hasCatalogChanged = !equal(
      values.syncCatalog.streams
        .filter((s) => s.config?.selected)
        .sort(naturalComparatorBy((syncStream) => syncStream.stream?.name ?? "")),
      initialConnection.syncCatalog.streams
        .filter((s) => s.config?.selected)
        .sort(naturalComparatorBy((syncStream) => syncStream.stream?.name ?? ""))
    );
    // Whenever the catalog changed show a warning to the user, that we're about to reset their data.
    // Given them a choice to opt-out in which case we'll be sending skipRefresh: true to the update
    // endpoint.
    if (hasCatalogChanged) {
      const stateType = await connectionService.getStateType(connectionId);
      const result = await openModal<boolean>({
        title: formatMessage({ id: "connection.resetModalTitle" }),
        size: "md",
        content: (props) => <ResetWarningModal {...props} stateType={stateType} />,
      });
      if (result.type === "canceled") {
        throw new ModalCancel();
      }
      // Save the connection taking into account the correct skipRefresh value from the dialog choice.
      await saveConnection(values, { skipReset: !result.reason });
    } else {
      // The catalog hasn't changed. We don't need to ask for any confirmation and can simply save.
      await saveConnection(values, { skipReset: true });
    }
  };

  // TODO: Move this into the service next
  const refreshSourceSchema = async () => {
    setSaved(false);
    setActiveUpdatingSchemaMode(true);
    const { catalogDiff, syncCatalog } = await refreshCatalog();
    if (catalogDiff?.transforms && catalogDiff.transforms.length > 0) {
      await openModal<void>({
        title: formatMessage({ id: "connection.updateSchema.completed" }),
        preventCancel: true,
        content: ({ onClose }) => (
          <CatalogDiffModal catalogDiff={catalogDiff} catalog={syncCatalog} onClose={onClose} />
        ),
      });
    }
  };

  const onRefreshSourceSchema = async () => {
    if (formDirty) {
      // The form is dirty so we show a warning before proceeding.
      openConfirmationModal({
        title: "connection.updateSchema.formChanged.title",
        text: "connection.updateSchema.formChanged.text",
        submitButtonText: "connection.updateSchema.formChanged.confirm",
        onSubmit: () => {
          closeConfirmationModal();
          refreshSourceSchema();
        },
      });
    } else {
      // The form is not dirty so we can directly refresh the source schema.
      refreshSourceSchema();
    }
  };

  const onCancelConnectionFormEdit = () => {
    setSaved(false);
    setActiveUpdatingSchemaMode(false);
  };

  return (
    <Content>
      {!isRefreshingCatalog && connection ? (
        <ConnectionFormServiceProvider
          connection={connection}
          mode={connection?.status !== ConnectionStatus.deprecated ? "edit" : "readonly"}
          onSubmit={onSubmitForm}
          onCancel={onCancelConnectionFormEdit}
          formId={formId}
          formDirty={formDirty}
        >
          <ConnectionForm
            successMessage={saved && <FormattedMessage id="form.changesSaved" />}
            canSubmitUntouchedForm={activeUpdatingSchemaMode}
            additionalSchemaControl={
              <Button onClick={onRefreshSourceSchema} type="button" secondary>
                <TryArrow icon={faSyncAlt} />
                <FormattedMessage id="connection.updateSchema" />
              </Button>
            }
          />
        </ConnectionFormServiceProvider>
      ) : (
        <LoadingSchema />
      )}
    </Content>
  );
};
