import { Form, Formik, FormikHelpers } from "formik";
import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { SchemaError } from "components/CreateConnection/SchemaError";
import LoadingSchema from "components/LoadingSchema";

import { Action, Namespace } from "core/analytics";
import { getFrequencyFromScheduleData } from "core/analytics/utils";
import { toWebBackendConnectionUpdate } from "core/domain/connection";
import { PageTrackingCodes, useAnalyticsService, useTrackPage } from "hooks/services/Analytics";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import {
  tidyConnectionFormValues,
  useConnectionFormService,
} from "hooks/services/ConnectionForm/ConnectionFormService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useModalService } from "hooks/services/Modal";
import { useConnectionService, ValuesProps } from "hooks/services/useConnectionHook";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import { equal } from "utils/objects";
import { useConfirmCatalogDiff } from "views/Connection/CatalogDiffModal/useConfirmCatalogDiff";
import EditControls from "views/Connection/ConnectionForm/components/EditControls";
import { ConnectionFormFields } from "views/Connection/ConnectionForm/ConnectionFormFields";
import {
  createConnectionValidationSchema,
  FormikConnectionFormValues,
} from "views/Connection/ConnectionForm/formConfig";

import styles from "./ConnectionReplicationTab.module.scss";
import { ResetWarningModal } from "./ResetWarningModal";

export const ConnectionReplicationTab: React.FC = () => {
  const analyticsService = useAnalyticsService();
  const connectionService = useConnectionService();
  const workspaceId = useCurrentWorkspaceId();

  const { formatMessage } = useIntl();
  const { openModal } = useModalService();

  const [saved, setSaved] = useState(false);

  const { connection, schemaRefreshing, schemaHasBeenRefreshed, updateConnection, setSchemaHasBeenRefreshed } =
    useConnectionEditService();
  const { initialValues, mode, schemaError, getErrorMessage, setSubmitError } = useConnectionFormService();
  const allowSubOneHourCronExpressions = useFeature(FeatureItem.AllowSyncSubOneHourCronExpressions);

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
      const formValues = tidyConnectionFormValues(
        values,
        workspaceId,
        mode,
        allowSubOneHourCronExpressions,
        connection.operations
      );

      // Detect whether the catalog has any differences in its enabled streams compared to the original one.
      // This could be due to user changes (e.g. in the sync mode) or due to new/removed
      // streams due to a "refreshed source schema".
      const catalogHasChanged = !equal(
        formValues.syncCatalog.streams.filter((s) => s.config?.selected),
        connection.syncCatalog.streams.filter((s) => s.config?.selected)
      );

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
            // We also want to skip the reset sync if the connection is not in an "active" status
            await saveConnection(formValues, {
              skipReset: !result.reason || connection.status !== "active",
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
        setSchemaHasBeenRefreshed(false);
      } catch (e) {
        setSubmitError(e);
      }
    },
    [
      connection.connectionId,
      connection.operations,
      connection.status,
      connection.syncCatalog.streams,
      connectionService,
      formatMessage,
      mode,
      openModal,
      saveConnection,
      setSchemaHasBeenRefreshed,
      setSubmitError,
      workspaceId,
      allowSubOneHourCronExpressions,
    ]
  );

  useConfirmCatalogDiff();

  return (
    <div className={styles.content}>
      {schemaError && !schemaRefreshing ? (
        <SchemaError schemaError={schemaError} />
      ) : !schemaRefreshing && connection ? (
        <Formik
          initialValues={initialValues}
          validationSchema={createConnectionValidationSchema({ mode, allowSubOneHourCronExpressions })}
          onSubmit={onFormSubmit}
          enableReinitialize
        >
          {({ values, isSubmitting, isValid, dirty, resetForm }) => (
            <Form>
              <ConnectionFormFields values={values} isSubmitting={isSubmitting} dirty={dirty} />
              <EditControls
                isSubmitting={isSubmitting}
                submitDisabled={!isValid}
                dirty={dirty}
                resetForm={async () => {
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
    </div>
  );
};
