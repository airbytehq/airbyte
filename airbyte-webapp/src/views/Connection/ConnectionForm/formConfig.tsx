import { useMemo } from "react";
import { useIntl } from "react-intl";
import * as yup from "yup";

import { DropDownRow } from "components";

import { frequencyConfig } from "config/frequencyConfig";
import { SyncSchema } from "core/domain/catalog";
import {
  isDbtTransformation,
  isNormalizationTransformation,
  NormalizationType,
} from "core/domain/connection/operation";
import { SOURCE_NAMESPACE_TAG } from "core/domain/connector/source";
import {
  ConnectionScheduleData,
  ConnectionScheduleType,
  DestinationDefinitionSpecificationRead,
  DestinationSyncMode,
  NamespaceDefinitionType,
  OperationCreate,
  OperationRead,
  OperatorType,
  SyncMode,
  WebBackendConnectionRead,
} from "core/request/AirbyteClient";
import { ValuesProps } from "hooks/services/useConnectionHook";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import calculateInitialCatalog from "./calculateInitialCatalog";

interface FormikConnectionFormValues {
  name?: string;
  scheduleType?: ConnectionScheduleType | null;
  scheduleData?: ConnectionScheduleData | null;
  prefix: string;
  syncCatalog: SyncSchema;
  namespaceDefinition?: NamespaceDefinitionType;
  namespaceFormat: string;
  transformations?: OperationRead[];
  normalization?: NormalizationType;
}

type ConnectionFormValues = ValuesProps;

const SUPPORTED_MODES: Array<[SyncMode, DestinationSyncMode]> = [
  [SyncMode.incremental, DestinationSyncMode.append_dedup],
  [SyncMode.full_refresh, DestinationSyncMode.overwrite],
  [SyncMode.incremental, DestinationSyncMode.append],
  [SyncMode.full_refresh, DestinationSyncMode.append],
];

const DEFAULT_SCHEDULE: ConnectionScheduleData = {
  basicSchedule: {
    units: 24,
    timeUnit: "hours",
  },
};

function useDefaultTransformation(): OperationCreate {
  const workspace = useCurrentWorkspace();
  return {
    name: "My dbt transformations",
    workspaceId: workspace.workspaceId,
    operatorConfiguration: {
      operatorType: OperatorType.dbt,
      dbt: {
        gitRepoUrl: "", // TODO: Does this need a value?
        dockerImage: "fishtownanalytics/dbt:1.0.0",
        dbtArguments: "run",
      },
    },
  };
}

const connectionValidationSchema = yup
  .object({
    name: yup.string().required("form.empty.error"),
    scheduleType: yup.string().oneOf([ConnectionScheduleType.manual, ConnectionScheduleType.basic]),
    scheduleData: yup
      .object({
        basicSchedule: yup
          .object({
            units: yup.number().required("form.empty.error"),
            timeUnit: yup.string().required("form.empty.error"),
          })
          .nullable()
          .defined("form.empty.error"),
      })
      .nullable()
      .defined("form.empty.error"),
    namespaceDefinition: yup
      .string()
      .oneOf([
        NamespaceDefinitionType.source,
        NamespaceDefinitionType.destination,
        NamespaceDefinitionType.customformat,
      ])
      .required("form.empty.error"),
    namespaceFormat: yup.string().when("namespaceDefinition", {
      is: NamespaceDefinitionType.customformat,
      then: yup.string().required("form.empty.error"),
    }),
    prefix: yup.string(),
    syncCatalog: yup.object({
      streams: yup.array().of(
        yup.object({
          id: yup
            .string()
            // This is required to get rid of id fields we are using to detect stream for edition
            .when("$isRequest", (isRequest: boolean, schema: yup.StringSchema) =>
              isRequest ? schema.strip(true) : schema
            ),
          stream: yup.object(),
          config: yup
            .object({
              selected: yup.boolean(),
              syncMode: yup.string(),
              destinationSyncMode: yup.string(),
              primaryKey: yup.array().of(yup.array().of(yup.string())),
              cursorField: yup.array().of(yup.string()).defined(),
            })
            .test({
              name: "connectionSchema.config.validator",
              // eslint-disable-next-line no-template-curly-in-string
              message: "${path} is wrong",
              test(value) {
                if (!value.selected) {
                  return true;
                }
                if (DestinationSyncMode.append_dedup === value.destinationSyncMode) {
                  // it's possible that primaryKey array is always present
                  // however yup couldn't determine type correctly even with .required() call
                  if (value.primaryKey?.length === 0) {
                    return this.createError({
                      message: "connectionForm.primaryKey.required",
                      path: `schema.streams[${this.parent.id}].config.primaryKey`,
                    });
                  }
                }

                if (SyncMode.incremental === value.syncMode) {
                  if (
                    !this.parent.stream.sourceDefinedCursor &&
                    // it's possible that cursorField array is always present
                    // however yup couldn't determine type correctly even with .required() call
                    value.cursorField?.length === 0
                  ) {
                    return this.createError({
                      message: "connectionForm.cursorField.required",
                      path: `schema.streams[${this.parent.id}].config.cursorField`,
                    });
                  }
                }
                return true;
              },
            }),
        })
      ),
    }),
  })
  .noUnknown();

/**
 * Returns {@link Operation}[]
 *
 * Maps UI representation of Transformation and Normalization
 * into API's {@link Operation} representation.
 *
 * Always puts normalization as first operation
 * @param values
 * @param initialOperations
 * @param workspaceId
 */
function mapFormPropsToOperation(
  values: {
    transformations?: OperationRead[];
    normalization?: NormalizationType;
  },
  initialOperations: OperationRead[] = [],
  workspaceId: string
): OperationCreate[] {
  const newOperations: OperationCreate[] = [];

  if (values.normalization) {
    if (values.normalization !== NormalizationType.raw) {
      const normalizationOperation = initialOperations.find(isNormalizationTransformation);

      if (normalizationOperation) {
        newOperations.push(normalizationOperation);
      } else {
        newOperations.push({
          name: "Normalization",
          workspaceId,
          operatorConfiguration: {
            operatorType: OperatorType.normalization,
            normalization: {
              option: values.normalization,
            },
          },
        });
      }
    }
  }

  if (values.transformations) {
    newOperations.push(...values.transformations);
  }

  return newOperations;
}

const getInitialTransformations = (operations: OperationCreate[]): OperationRead[] =>
  operations?.filter(isDbtTransformation) ?? [];

const getInitialNormalization = (
  operations?: Array<OperationRead | OperationCreate>,
  isEditMode?: boolean
): NormalizationType => {
  const initialNormalization =
    operations?.find(isNormalizationTransformation)?.operatorConfiguration?.normalization?.option;

  return initialNormalization
    ? NormalizationType[initialNormalization]
    : isEditMode
    ? NormalizationType.raw
    : NormalizationType.basic;
};

const useInitialValues = (
  connection:
    | WebBackendConnectionRead
    | (Partial<WebBackendConnectionRead> & Pick<WebBackendConnectionRead, "syncCatalog" | "source" | "destination">),
  destDefinition: DestinationDefinitionSpecificationRead,
  isEditMode?: boolean
): FormikConnectionFormValues => {
  const initialSchema = useMemo(
    () =>
      calculateInitialCatalog(connection.syncCatalog, destDefinition?.supportedDestinationSyncModes || [], isEditMode),
    [connection.syncCatalog, destDefinition, isEditMode]
  );

  return useMemo(() => {
    const initialValues: FormikConnectionFormValues = {
      name: connection.name ?? `${connection.source.name} <> ${connection.destination.name}`,
      syncCatalog: initialSchema,
      scheduleData: connection.connectionId ? connection.scheduleData ?? null : DEFAULT_SCHEDULE,
      prefix: connection.prefix || "",
      namespaceDefinition: connection.namespaceDefinition || NamespaceDefinitionType.source,
      namespaceFormat: connection.namespaceFormat ?? SOURCE_NAMESPACE_TAG,
    };

    const operations = connection.operations ?? [];

    if (destDefinition.supportsDbt) {
      initialValues.transformations = getInitialTransformations(operations);
    }

    if (destDefinition.supportsNormalization) {
      initialValues.normalization = getInitialNormalization(operations, isEditMode);
    }

    return initialValues;
  }, [initialSchema, connection, isEditMode, destDefinition]);
};

const useFrequencyDropdownData = (
  additionalFrequency: WebBackendConnectionRead["scheduleData"]
): DropDownRow.IDataItem[] => {
  const { formatMessage } = useIntl();

  return useMemo(() => {
    const frequencies = [...frequencyConfig];
    if (additionalFrequency?.basicSchedule) {
      const additionalFreqAlreadyPresent = frequencies.some(
        (frequency) =>
          frequency?.timeUnit === additionalFrequency.basicSchedule?.timeUnit &&
          frequency?.units === additionalFrequency.basicSchedule?.units
      );
      if (!additionalFreqAlreadyPresent) {
        frequencies.push(additionalFrequency.basicSchedule);
      }
    }

    return frequencies.map((frequency) => ({
      value: frequency,
      label: frequency
        ? formatMessage(
            {
              id: `form.every.${frequency.timeUnit}`,
            },
            { value: frequency.units }
          )
        : formatMessage({ id: "frequency.manual" }),
    }));
  }, [formatMessage, additionalFrequency]);
};

export type { ConnectionFormValues, FormikConnectionFormValues };
export {
  connectionValidationSchema,
  useInitialValues,
  useFrequencyDropdownData,
  mapFormPropsToOperation,
  SUPPORTED_MODES,
  useDefaultTransformation,
  getInitialNormalization,
  getInitialTransformations,
};
