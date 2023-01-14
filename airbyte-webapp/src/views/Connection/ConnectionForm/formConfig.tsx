import { useMemo } from "react";
import { useIntl } from "react-intl";
import * as yup from "yup";

import { DropDownOptionDataItem } from "components/ui/DropDown";

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
  Geography,
  NamespaceDefinitionType,
  NonBreakingChangesPreference,
  OperationCreate,
  OperationRead,
  OperatorType,
  SyncMode,
  WebBackendConnectionRead,
} from "core/request/AirbyteClient";
import { ConnectionFormMode, ConnectionOrPartialConnection } from "hooks/services/ConnectionForm/ConnectionFormService";
import { ValuesProps } from "hooks/services/useConnectionHook";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { validateCronExpression, validateCronFrequencyOneHourOrMore } from "utils/cron";

import calculateInitialCatalog from "./calculateInitialCatalog";

export interface FormikConnectionFormValues {
  name?: string;
  scheduleType?: ConnectionScheduleType | null;
  scheduleData?: ConnectionScheduleData | null;
  nonBreakingChangesPreference?: NonBreakingChangesPreference | null;
  prefix: string;
  syncCatalog: SyncSchema;
  namespaceDefinition?: NamespaceDefinitionType;
  namespaceFormat: string;
  transformations?: OperationRead[];
  normalization?: NormalizationType;
  geography: Geography;
}

export type ConnectionFormValues = ValuesProps;

export const SUPPORTED_MODES: Array<[SyncMode, DestinationSyncMode]> = [
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

export function useDefaultTransformation(): OperationCreate {
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

interface CreateConnectionValidationSchemaArgs {
  allowSubOneHourCronExpressions: boolean;
  mode: ConnectionFormMode;
  isAutoDetectSchemaChangesEnabled: boolean;
}

export const createConnectionValidationSchema = ({
  mode,
  allowSubOneHourCronExpressions,
  isAutoDetectSchemaChangesEnabled,
}: CreateConnectionValidationSchemaArgs) =>
  yup
    .object({
      // The connection name during Editing is handled separately from the form
      name: mode === "create" ? yup.string().required("form.empty.error") : yup.string().notRequired(),
      geography: yup.mixed<Geography>().oneOf(Object.values(Geography)),
      scheduleType: yup
        .string()
        .oneOf([ConnectionScheduleType.manual, ConnectionScheduleType.basic, ConnectionScheduleType.cron]),
      scheduleData: yup.mixed().when("scheduleType", (scheduleType) => {
        if (scheduleType === ConnectionScheduleType.basic) {
          return yup.object({
            basicSchedule: yup
              .object({
                units: yup.number().required("form.empty.error"),
                timeUnit: yup.string().required("form.empty.error"),
              })
              .defined("form.empty.error"),
          });
        } else if (scheduleType === ConnectionScheduleType.manual) {
          return yup.mixed().notRequired();
        }

        return yup.object({
          cron: yup
            .object({
              cronExpression: yup
                .string()
                .trim()
                .required("form.empty.error")
                .test("validCron", "form.cronExpression.error", validateCronExpression)
                .test(
                  "validCronFrequency",
                  "form.cronExpression.underOneHourNotAllowed",
                  (expression) => allowSubOneHourCronExpressions || validateCronFrequencyOneHourOrMore(expression)
                ),
              cronTimeZone: yup.string().required("form.empty.error"),
            })
            .defined("form.empty.error"),
        });
      }),
      nonBreakingChangesPreference: isAutoDetectSchemaChangesEnabled
        ? yup.mixed().oneOf(Object.values(NonBreakingChangesPreference)).required("form.empty.error")
        : yup.mixed().notRequired(),

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
        then: yup.string().trim().required("form.empty.error"),
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
export function mapFormPropsToOperation(
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

export const getInitialTransformations = (operations: OperationCreate[]): OperationRead[] =>
  operations?.filter(isDbtTransformation) ?? [];

export const getInitialNormalization = (
  operations?: Array<OperationRead | OperationCreate>,
  isNotCreateMode?: boolean
): NormalizationType => {
  const initialNormalization =
    operations?.find(isNormalizationTransformation)?.operatorConfiguration?.normalization?.option;

  return initialNormalization
    ? NormalizationType[initialNormalization]
    : isNotCreateMode
    ? NormalizationType.raw
    : NormalizationType.basic;
};

export const useInitialValues = (
  connection: ConnectionOrPartialConnection,
  destDefinition: DestinationDefinitionSpecificationRead,
  isNotCreateMode?: boolean
): FormikConnectionFormValues => {
  const workspace = useCurrentWorkspace();
  const { catalogDiff } = connection;

  const newStreamDescriptors = catalogDiff?.transforms
    .filter((transform) => transform.transformType === "add_stream")
    .map((stream) => stream.streamDescriptor);

  const initialSchema = useMemo(
    () =>
      calculateInitialCatalog(
        connection.syncCatalog,
        destDefinition?.supportedDestinationSyncModes || [],
        isNotCreateMode,
        newStreamDescriptors
      ),
    [connection.syncCatalog, destDefinition?.supportedDestinationSyncModes, isNotCreateMode, newStreamDescriptors]
  );

  return useMemo(() => {
    const initialValues: FormikConnectionFormValues = {
      syncCatalog: initialSchema,
      scheduleType: connection.connectionId ? connection.scheduleType : ConnectionScheduleType.basic,
      scheduleData: connection.connectionId ? connection.scheduleData ?? null : DEFAULT_SCHEDULE,
      nonBreakingChangesPreference: connection.nonBreakingChangesPreference ?? NonBreakingChangesPreference.ignore,
      prefix: connection.prefix || "",
      namespaceDefinition: connection.namespaceDefinition || NamespaceDefinitionType.source,
      namespaceFormat: connection.namespaceFormat ?? SOURCE_NAMESPACE_TAG,
      geography: connection.geography || workspace.defaultGeography || "auto",
    };

    // Is Create Mode
    if (!isNotCreateMode) {
      initialValues.name = connection.name ?? `${connection.source.name} <> ${connection.destination.name}`;
    }

    const operations = connection.operations ?? [];

    if (destDefinition.supportsDbt) {
      initialValues.transformations = getInitialTransformations(operations);
    }

    if (destDefinition.supportsNormalization) {
      initialValues.normalization = getInitialNormalization(operations, isNotCreateMode);
    }

    return initialValues;
  }, [
    connection.connectionId,
    connection.destination.name,
    connection.geography,
    connection.name,
    connection.namespaceDefinition,
    connection.namespaceFormat,
    connection.nonBreakingChangesPreference,
    connection.operations,
    connection.prefix,
    connection.scheduleData,
    connection.scheduleType,
    connection.source.name,
    destDefinition.supportsDbt,
    destDefinition.supportsNormalization,
    initialSchema,
    isNotCreateMode,
    workspace,
  ]);
};

export const useFrequencyDropdownData = (
  additionalFrequency: WebBackendConnectionRead["scheduleData"]
): DropDownOptionDataItem[] => {
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

    const basicFrequencies = frequencies.map((frequency) => ({
      value: frequency,
      label: formatMessage(
        {
          id: `form.every.${frequency.timeUnit}`,
        },
        { value: frequency.units }
      ),
    }));

    // Add Manual and Custom to the frequencies list
    const customFrequency = formatMessage({
      id: "frequency.cron",
    });
    const manualFrequency = formatMessage({
      id: "frequency.manual",
    });
    const otherFrequencies = [
      {
        label: manualFrequency,
        value: manualFrequency.toLowerCase(),
      },
      {
        label: customFrequency,
        value: customFrequency.toLowerCase(),
      },
    ];

    return [...otherFrequencies, ...basicFrequencies];
  }, [formatMessage, additionalFrequency]);
};
