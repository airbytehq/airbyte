import { Form, Formik, FormikHelpers } from "formik";
import React, { useCallback, useEffect, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useUnmount } from "react-use";
import styled from "styled-components";

import LoadingSchema from "components/LoadingSchema";

import { getFrequencyType } from "config/utils";
import { Action, Namespace } from "core/analytics";
import { toWebBackendConnectionUpdate } from "core/domain/connection";
import { PageTrackingCodes, useAnalyticsService, useTrackPage } from "hooks/services/Analytics";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import {
  tidyConnectionFormValues,
  useConnectionFormService,
} from "hooks/services/ConnectionForm/ConnectionFormService";
import { useModalService } from "hooks/services/Modal";
import { useConnectionService, useUpdateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import { equal, naturalComparatorBy } from "utils/objects";
import { CatalogDiffModal } from "views/Connection/CatalogDiffModal/CatalogDiffModal";
import EditControls from "views/Connection/ConnectionForm/components/EditControls";
import { ConnectionFormFields } from "views/Connection/ConnectionForm/ConnectionFormFields";
import { connectionValidationSchema, FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

import { ResetWarningModal } from "./ResetWarningModal";

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
  const { closeConfirmationModal } = useConfirmationModalService();
  const [saved, setSaved] = useState(false);

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_REPLICATION);

  const { mutateAsync: updateConnection } = useUpdateConnection();

  const {
    connection,
    schemaRefreshing,
    schemaHasBeenRefreshed,
    setConnection,
    setSchemaHasBeenRefreshed,
    refreshSchema,
  } = useConnectionEditService();

  const { initialValues, getErrorMessage, setSubmitError } = useConnectionFormService();

  const workspaceId = useCurrentWorkspaceId();

  useUnmount(() => {
    closeModal();
    closeConfirmationModal();
  });

  const saveConnection = useCallback(
    async (values: ValuesProps, { skipReset }: { skipReset: boolean }) => {
      if (schemaRefreshing) {
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
    },
    [analyticsService, connection, schemaRefreshing, setConnection, updateConnection]
  );

  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues, _: FormikHelpers<FormikConnectionFormValues>) => {
      const formValues = tidyConnectionFormValues(values, workspaceId, connection.operations);

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
            // Save the connection taking into account the correct skipRefresh value from the dialog choice.
            await saveConnection(formValues, { skipReset: !result.reason });
          } else {
            // We don't want to set saved to true or schema has been refreshed to false.
            return;
          }
        } else {
          // The catalog hasn't changed. We don't need to ask for any confirmation and can simply save.
          await saveConnection(formValues, { skipReset: true });
        }

        setSaved(true);
        setSchemaHasBeenRefreshed(false);
      } catch (e) {
        setSubmitError(e);
      }
    },
    [
      connection.connectionId,
      connection.operations,
      connection.syncCatalog.streams,
      connectionService,
      formatMessage,
      openModal,
      saveConnection,
      setSchemaHasBeenRefreshed,
      setSubmitError,
      workspaceId,
    ]
  );

  useEffect(() => {
    // If we have a catalogDiff we always want to show the modal
    const { catalogDiff, syncCatalog } = connection;
    if (catalogDiff?.transforms && catalogDiff.transforms?.length > 0) {
      openModal<void>({
        title: formatMessage({ id: "connection.updateSchema.completed" }),
        preventCancel: true,
        content: ({ onClose }) => (
          <CatalogDiffModal catalogDiff={catalogDiff} catalog={syncCatalog} onClose={onClose} />
        ),
      });
    }
  }, [connection, formatMessage, openModal]);

  return (
    <Content>
      {!schemaRefreshing && connection ? (
        <Formik initialValues={initialValues} validationSchema={connectionValidationSchema} onSubmit={onFormSubmit}>
          {({ values, isSubmitting, isValid, dirty, resetForm }) => (
            <Form>
              <ConnectionFormFields values={values} isSubmitting={isSubmitting} refreshSchema={refreshSchema} />
              <EditControls
                isSubmitting={isSubmitting}
                dirty={dirty}
                resetForm={() => {
                  resetForm();
                  setSchemaHasBeenRefreshed(false);
                }}
                successMessage={saved && !dirty && <FormattedMessage id="form.changesSaved" />}
                errorMessage={getErrorMessage(isValid, dirty)}
                enableControls={schemaHasBeenRefreshed || dirty}
              />
            </Form>
          )}
        </Formik>
      ) : (
        <LoadingSchema />
      )}
    </Content>
  );
};
