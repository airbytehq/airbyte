import { FormikHelpers } from "formik";
import React, { useEffect, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useUnmount } from "react-use";
import styled from "styled-components";

import { Button, LabeledSwitch, ModalBody, ModalFooter } from "components";
import LoadingSchema from "components/LoadingSchema";

import { getFrequencyType } from "config/utils";
import { Action, Namespace } from "core/analytics";
import { toWebBackendConnectionUpdate } from "core/domain/connection";
import { ConnectionStateType } from "core/request/AirbyteClient";
import { PageTrackingCodes, useAnalyticsService, useTrackPage } from "hooks/services/Analytics";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { tidyConnectionFormValues, useConnectionFormService } from "hooks/services/Connection/ConnectionFormService";
import { useModalService } from "hooks/services/Modal";
import { useConnectionService, useUpdateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import { equal, naturalComparatorBy } from "utils/objects";
import { CatalogDiffModal } from "views/Connection/CatalogDiffModal/CatalogDiffModal";
import { ConnectionForm } from "views/Connection/ConnectionForm";
import { FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

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

export const ConnectionReplication: React.FC = () => {
  const analyticsService = useAnalyticsService();
  const connectionService = useConnectionService();
  const { formatMessage } = useIntl();

  const { openModal, closeModal } = useModalService();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_REPLICATION);

  const [hasBeenSaved, setHasBeenSaved] = useState(false);

  const { mutateAsync: updateConnection } = useUpdateConnection();

  const {
    connection,
    isRefreshingCatalog,
    connectionDirty,
    schemaHasBeenRefreshed,
    refreshConnectionCatalog,
    setSubmitError,
    setConnection,
    setSchemaHasBeenRefreshed,
  } = useConnectionFormService();

  const workspaceId = useCurrentWorkspaceId();

  useUnmount(() => {
    closeModal();
    closeConfirmationModal();
  });

  const saveConnection = async (values: ValuesProps, { skipReset }: { skipReset: boolean }) => {
    if (isRefreshingCatalog) {
      return;
    }
    const connectionAsUpdate = toWebBackendConnectionUpdate(connection);

    const updatedConnection = await updateConnection({
      ...connectionAsUpdate,
      ...values,
      connectionId: connection.connectionId,
      skipReset,
    });

    if (!equal(values.syncCatalog, connection.syncCatalog)) {
      analyticsService.track(Namespace.CONNECTION, Action.EDIT_SCHEMA, {
        actionDescription: "Connection saved with catalog changes",
        connector_source: connection.source.sourceName,
        connector_source_definition_id: connection.source.sourceDefinitionId,
        connector_destination: connection.destination.destinationName,
        connector_destination_definition_id: connection.destination.destinationDefinitionId,
        frequency: getFrequencyType(connection.scheduleData?.basicSchedule),
      });
    }

    setConnection(updatedConnection);
    setHasBeenSaved(true);
  };

  const onSubmitForm = async (values: FormikConnectionFormValues, _: FormikHelpers<FormikConnectionFormValues>) => {
    const formValues = tidyConnectionFormValues(values, connection.operations, workspaceId);

    // Detect whether the catalog has any differences in its enabled streams compared to the original one.
    // This could be due to user changes (e.g. in the sync mode) or due to new/removed
    // streams due to a "refreshed source schema".
    const hasCatalogChanged = !equal(
      formValues.syncCatalog.streams
        .filter((s) => s.config?.selected)
        .sort(naturalComparatorBy((syncStream) => syncStream.stream?.name ?? "")),
      connection.syncCatalog.streams
        .filter((s) => s.config?.selected)
        .sort(naturalComparatorBy((syncStream) => syncStream.stream?.name ?? ""))
    );

    setSubmitError(null);

    // Whenever the catalog changed show a warning to the user, that we're about to reset their data.
    // Given them a choice to opt-out in which case we'll be sending skipRefresh: true to the update
    // endpoint.
    try {
      if (hasCatalogChanged) {
        const stateType = await connectionService.getStateType(connection.connectionId);
        const result = await openModal<boolean>({
          title: formatMessage({ id: "connection.resetModalTitle" }),
          size: "md",
          content: (props) => <ResetWarningModal {...props} stateType={stateType} />,
        });
        if (result.type !== "canceled") {
          await saveConnection(formValues, { skipReset: !result.reason });
        }
        // Save the connection taking into account the correct skipRefresh value from the dialog choice.
      } else {
        // The catalog hasn't changed. We don't need to ask for any confirmation and can simply save.
        await saveConnection(formValues, { skipReset: true });
      }
      setSchemaHasBeenRefreshed(false);
    } catch (e) {
      setSubmitError(e);
    }
  };

  useEffect(() => {
    const { catalogDiff, syncCatalog } = connection;
    if (catalogDiff?.transforms && catalogDiff.transforms.length > 0) {
      openModal<void>({
        title: formatMessage({ id: "connection.updateSchema.completed" }),
        preventCancel: true,
        content: ({ onClose }) => (
          <CatalogDiffModal catalogDiff={catalogDiff} catalog={syncCatalog} onClose={onClose} />
        ),
      });
    }
  }, [connection, formatMessage, openModal]);

  useEffect(() => {
    if (connectionDirty) {
      setHasBeenSaved(false);
    }
  }, [connectionDirty]);

  const onRefreshSourceSchema = async () => {
    if (connectionDirty) {
      // The form is dirty so we show a warning before proceeding.
      openConfirmationModal({
        title: "connection.updateSchema.formChanged.title",
        text: "connection.updateSchema.formChanged.text",
        submitButtonText: "connection.updateSchema.formChanged.confirm",
        onSubmit: () => {
          closeConfirmationModal();
          refreshConnectionCatalog();
        },
      });
    } else {
      // The form is not dirty so we can directly refresh the source schema.
      refreshConnectionCatalog();
    }
  };

  const onCancelConnectionFormEdit = () => {
    setSchemaHasBeenRefreshed(false);
  };

  return (
    <Content>
      {!isRefreshingCatalog && connection ? (
        <ConnectionForm
          /* successMessage could be replaced with a toast */
          successMessage={hasBeenSaved && <FormattedMessage id="form.changesSaved" />}
          canSubmitUntouchedForm={schemaHasBeenRefreshed}
          onFormSubmit={onSubmitForm}
          onCancel={onCancelConnectionFormEdit}
          onRefreshSourceSchema={onRefreshSourceSchema}
        />
      ) : (
        <LoadingSchema />
      )}
    </Content>
  );
};
