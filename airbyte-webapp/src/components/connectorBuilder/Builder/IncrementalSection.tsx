import { useField } from "formik";
import { useIntl } from "react-intl";

import { ControlLabels } from "components/LabeledControl";

import { DatetimeBasedCursor, RequestOption } from "core/request/ConnectorManifest";

import { BuilderCard } from "./BuilderCard";
import { BuilderFieldWithInputs } from "./BuilderFieldWithInputs";
import { BuilderOptional } from "./BuilderOptional";
import { RequestOptionFields } from "./RequestOptionFields";
import { ToggleGroupField } from "./ToggleGroupField";

interface IncrementalSectionProps {
  streamFieldPath: (fieldPath: string) => string;
  currentStreamIndex: number;
}

export const IncrementalSection: React.FC<IncrementalSectionProps> = ({ streamFieldPath, currentStreamIndex }) => {
  const { formatMessage } = useIntl();
  const [field, , helpers] = useField<DatetimeBasedCursor | undefined>(streamFieldPath("incrementalSync"));

  const handleToggle = (newToggleValue: boolean) => {
    if (newToggleValue) {
      helpers.setValue({
        type: "DatetimeBasedCursor",
        cursor_field: "",
        datetime_format: "",
        cursor_granularity: "",
        end_datetime: "",
        start_datetime: "",
        step: "",
      });
    } else {
      helpers.setValue(undefined);
    }
  };
  const toggledOn = field.value !== undefined;

  return (
    <BuilderCard
      toggleConfig={{
        label: (
          <ControlLabels
            label="Incremental sync"
            infoTooltipContent="Configure how to fetch data incrementally based on a time field in your data"
          />
        ),
        toggledOn,
        onToggle: handleToggle,
      }}
      copyConfig={{
        path: "incrementalSync",
        currentStreamIndex,
        copyFromLabel: formatMessage({ id: "connectorBuilder.copyToIncrementalTitle" }),
        copyToLabel: formatMessage({ id: "connectorBuilder.copyFromIncrementalTitle" }),
      }}
    >
      <BuilderFieldWithInputs
        type="string"
        path={streamFieldPath("incrementalSync.cursor_field")}
        label="Cursor field"
        tooltip="Field on record to use as the cursor"
      />
      <BuilderFieldWithInputs
        type="string"
        path={streamFieldPath("incrementalSync.datetime_format")}
        label="Datetime format"
        tooltip="Specify the format of the start and end time, e.g. %Y-%m-%d"
      />
      <BuilderFieldWithInputs
        type="string"
        path={streamFieldPath("incrementalSync.cursor_granularity")}
        label="Cursor granularity"
        tooltip="Smallest increment the datetime format has (ISO 8601 duration) that will be used to ensure that the start of a slice does not overlap with the end of the previous one, e.g. for %Y-%m-%d the granularity should be P1D, for %Y-%m-%dT%H:%M:%SZ the granularity should be PT1S"
      />
      <BuilderFieldWithInputs
        type="string"
        path={streamFieldPath("incrementalSync.start_datetime")}
        label="Start datetime"
        tooltip="Start time to start slicing"
      />
      <BuilderFieldWithInputs
        type="string"
        path={streamFieldPath("incrementalSync.end_datetime")}
        label="End datetime"
        tooltip="End time to end slicing"
      />
      <BuilderFieldWithInputs
        type="string"
        path={streamFieldPath("incrementalSync.step")}
        label="Step"
        tooltip="Time interval (ISO 8601 duration) for which to break up stream into slices, e.g. P1D for daily slices"
      />
      <ToggleGroupField<RequestOption>
        label="Start time request option"
        tooltip="Optionally configures how the start datetime will be sent in requests to the source API"
        fieldPath={streamFieldPath("incrementalSync.start_time_option")}
        initialValues={{
          inject_into: "request_parameter",
          type: "RequestOption",
          field_name: "",
        }}
      >
        <RequestOptionFields
          path={streamFieldPath("incrementalSync.start_time_option")}
          descriptor="start datetime"
          excludePathInjection
        />
      </ToggleGroupField>
      <ToggleGroupField<RequestOption>
        label="End time request option"
        tooltip="Optionally configures how the end datetime will be sent in requests to the source API"
        fieldPath={streamFieldPath("incrementalSync.end_time_option")}
        initialValues={{
          inject_into: "request_parameter",
          type: "RequestOption",
          field_name: "",
        }}
      >
        <RequestOptionFields
          path={streamFieldPath("incrementalSync.end_time_option")}
          descriptor="end datetime"
          excludePathInjection
        />
      </ToggleGroupField>
      <BuilderOptional>
        <BuilderFieldWithInputs
          type="string"
          path={streamFieldPath("incrementalSync.lookback_window")}
          label="Lookback window"
          tooltip="Time interval (ISO 8601 duration) before the start_datetime to read data for, e.g. P1M for looking back one month"
          optional
        />
        <BuilderFieldWithInputs
          type="string"
          path={streamFieldPath("incrementalSync.partition_field_start")}
          label="Stream state field start"
          tooltip="Set which field on the stream state to use to determine the starting point"
          optional
        />
        <BuilderFieldWithInputs
          type="string"
          path={streamFieldPath("incrementalSync.partition_field_end")}
          label="Stream state field end"
          tooltip="Set which field on the stream state to use to determine the ending point"
          optional
        />
      </BuilderOptional>
    </BuilderCard>
  );
};
