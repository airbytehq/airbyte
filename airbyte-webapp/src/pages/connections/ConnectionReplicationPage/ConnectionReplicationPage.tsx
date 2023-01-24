import { Form, Formik, FormikHelpers, useFormikContext } from "formik";
import React, { useCallback, useEffect, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useUnmount } from "react-use";

import { ConnectionFormFields } from "components/connection/ConnectionForm/ConnectionFormFields";
import EditControls from "components/connection/ConnectionForm/EditControls";
import {
  FormikConnectionFormValues,
  useConnectionValidationSchema,
} from "components/connection/ConnectionForm/formConfig";
import { SchemaChangeBackdrop } from "components/connection/ConnectionForm/SchemaChangeBackdrop";
import { SchemaError } from "components/connection/CreateConnectionForm/SchemaError";
import LoadingSchema from "components/LoadingSchema";

import { Action, Namespace } from "core/analytics";
import { getFrequencyFromScheduleData } from "core/analytics/utils";
import { toWebBackendConnectionUpdate } from "core/domain/connection";
import { useConfirmCatalogDiff } from "hooks/connection/useConfirmCatalogDiff";
import { PageTrackingCodes, useAnalyticsService, useTrackPage } from "hooks/services/Analytics";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import {
  tidyConnectionFormValues,
  useConnectionFormService,
} from "hooks/services/ConnectionForm/ConnectionFormService";
import { useModalService } from "hooks/services/Modal";
import { useConnectionService, ValuesProps } from "hooks/services/useConnectionHook";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import { equal } from "utils/objects";

import styles from "./ConnectionReplicationPage.module.scss";
import { ResetWarningModal } from "./ResetWarningModal";

const ValidateFormOnSchemaRefresh: React.FC = () => {
  const { schemaHasBeenRefreshed } = useConnectionEditService();
  const { setTouched } = useFormikContext();

  useEffect(() => {
    if (schemaHasBeenRefreshed) {
      setTouched({ syncCatalog: true }, true);
    }
  }, [setTouched, schemaHasBeenRefreshed]);

  return null;
};

export const ConnectionReplicationPage: React.FC = () => {
  const analyticsService = useAnalyticsService();
  const connectionService = useConnectionService();
  const workspaceId = useCurrentWorkspaceId();

  const { formatMessage } = useIntl();
  const { openModal } = useModalService();

  const [saved, setSaved] = useState(false);

  const { connection, schemaRefreshing, schemaHasBeenRefreshed, updateConnection, discardRefreshedSchema } =
    useConnectionEditService();
  const { initialValues, mode, schemaError, getErrorMessage, setSubmitError } = useConnectionFormService();
  const validationSchema = useConnectionValidationSchema({ mode });

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_REPLICATION);

  const saveConnection = useCallback(
    async (
      values: ValuesProps,
      { skipReset, catalogHasChanged }: { skipReset: boolean; catalogHasChanged: boolean }
    ) => {
      const connectionAsUpdate = toWebBackendConnectionUpdate(connection);

      await updateConnection({
        ...connectionAsUpdate,
        ...values,
        connectionId: connection.connectionId,
        skipReset,
      });

      if (catalogHasChanged) {
        // TODO (https://github.com/airbytehq/airbyte/issues/17666): Move this into a useTrackChangedCatalog method (name pending) post Vlad's analytics hook work
        analyticsService.track(Namespace.CONNECTION, Action.EDIT_SCHEMA, {
          actionDescription: "Connection saved with catalog changes",
          connector_source: connection.source.sourceName,
          connector_source_definition_id: connection.source.sourceDefinitionId,
          connector_destination: connection.destination.destinationName,
          connector_destination_definition_id: connection.destination.destinationDefinitionId,
          frequency: getFrequencyFromScheduleData(connection.scheduleData),
        });
      }
    },
    [analyticsService, connection, updateConnection]
  );

  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues, _: FormikHelpers<FormikConnectionFormValues>) => {
      const formValues = tidyConnectionFormValues(values, workspaceId, validationSchema, connection.operations);

      // Check if the user refreshed the catalog and there was any change in a currently enabled stream
      const hasDiffInEnabledStream = connection.catalogDiff?.transforms.some(({ streamDescriptor }) => {
        // Find the stream for this transform in our form's syncCatalog
        const stream = formValues.syncCatalog.streams.find(
          ({ stream }) => streamDescriptor.name === stream?.name && streamDescriptor.namespace === stream.namespace
        );
        return stream?.config?.selected;
      });

      // Check if the user made any modifications to enabled streams compared to the ones in the latest connection
      // e.g. changed the sync mode of an enabled stream
      const hasUserChangesInEnabledStreams = !equal(
        formValues.syncCatalog.streams.filter((s) => s.config?.selected),
        connection.syncCatalog.streams.filter((s) => s.config?.selected)
      );

      const catalogHasChanged = hasDiffInEnabledStream || hasUserChangesInEnabledStreams;

      setSubmitError(null);

      // Whenever the catalog changed show a warning to the user, that we're about to reset their data.
      // Given them a choice to opt-out in which case we'll be sending skipReset: true to the update
      // endpoint.
      try {
        if (catalogHasChanged) {
          const stateType = await connectionService.getStateType(connection.connectionId);
          const result = await openModal<boolean>({
            title: formatMessage({ id: "connection.resetModalTitle" }),
            size: "md",
            content: (props) => <ResetWarningModal {...props} stateType={stateType} />,
          });
          if (result.type !== "canceled") {
            // Save the connection taking into account the correct skipReset value from the dialog choice.
            await saveConnection(formValues, {
              skipReset: !result.reason,
              catalogHasChanged,
            });
          } else {
            // We don't want to set saved to true or schema has been refreshed to false.
            return;
          }
        } else {
          // The catalog hasn't changed. We don't need to ask for any confirmation and can simply save.
          await saveConnection(formValues, { skipReset: true, catalogHasChanged });
        }

        setSaved(true);
      } catch (e) {
        setSubmitError(e);
      }
    },
    [
      workspaceId,
      validationSchema,
      connection.operations,
      connection.catalogDiff?.transforms,
      connection.syncCatalog.streams,
      connection.connectionId,
      setSubmitError,
      connectionService,
      openModal,
      formatMessage,
      saveConnection,
    ]
  );

  useConfirmCatalogDiff();

  useUnmount(() => {
    discardRefreshedSchema();
  });

  return (
    <div className={styles.content}>
      {schemaError && !schemaRefreshing ? (
        <SchemaError schemaError={schemaError} />
      ) : !schemaRefreshing && connection ? (
        <Formik
          initialStatus={{ editControlsVisible: true }}
          initialValues={initialValues}
          validationSchema={validationSchema}
          onSubmit={onFormSubmit}
          enableReinitialize
        >
          {({ values, isSubmitting, isValid, dirty, resetForm, status }) => (
            <SchemaChangeBackdrop>
              <Form>
                <ValidateFormOnSchemaRefresh />
                <ConnectionFormFields
                  values={values}
                  isSubmitting={isSubmitting}
                  dirty={dirty || schemaHasBeenRefreshed}
                />
                {status.editControlsVisible && (
                  <EditControls
                    isSubmitting={isSubmitting}
                    submitDisabled={!isValid}
                    dirty={dirty}
                    resetForm={async () => {
                      resetForm();
                      discardRefreshedSchema();
                    }}
                    successMessage={saved && !dirty && <FormattedMessage id="form.changesSaved" />}
                    errorMessage={getErrorMessage(isValid, dirty)}
                    enableControls={schemaHasBeenRefreshed || dirty}
                  />
                )}
              </Form>
            </SchemaChangeBackdrop>
          )}
        </Formik>
      ) : (
        <LoadingSchema />
      )}
    </div>
  );
};
