import { useField } from "formik";
import { useIntl } from "react-intl";

import { ControlLabels } from "components/LabeledControl";

import { RequestOption, SimpleRetrieverStreamSlicer } from "core/request/ConnectorManifest";

import { timeDeltaRegex } from "../types";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderOneOf } from "./BuilderOneOf";
import { BuilderOptional } from "./BuilderOptional";
import { InjectRequestOptionFields } from "./InjectRequestOptionFields";
import { ToggleGroupField } from "./ToggleGroupField";

interface StreamSlicerSectionProps {
  streamFieldPath: (fieldPath: string) => string;
  currentStreamIndex: number;
}

export const StreamSlicerSection: React.FC<StreamSlicerSectionProps> = ({ streamFieldPath, currentStreamIndex }) => {
  const { formatMessage } = useIntl();
  const [field, , helpers] = useField<SimpleRetrieverStreamSlicer | undefined>(streamFieldPath("streamSlicer"));

  const handleToggle = (newToggleValue: boolean) => {
    if (newToggleValue) {
      helpers.setValue({
        type: "ListStreamSlicer",
        slice_values: [],
        cursor_field: "",
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
            label="Stream slicer"
            infoTooltipContent="Configure how to partition a stream into subsets of records and iterate over the data"
          />
        ),
        toggledOn,
        onToggle: handleToggle,
      }}
      copyConfig={{
        path: "streamSlicer",
        currentStreamIndex,
        copyFromLabel: formatMessage({ id: "connectorBuilder.copyFromSlicerTitle" }),
        copyToLabel: formatMessage({ id: "connectorBuilder.copyToSlicerTitle" }),
      }}
    >
      <BuilderOneOf
        path={streamFieldPath("streamSlicer")}
        label="Mode"
        tooltip="Stream slicer method to use on this stream"
        options={[
          {
            label: "List",
            typeValue: "ListStreamSlicer",
            children: (
              <>
                <BuilderField
                  type="array"
                  path={streamFieldPath("streamSlicer.slice_values")}
                  label="Slice values"
                  tooltip="List of values to iterate over"
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.cursor_field")}
                  label="Cursor field"
                  tooltip="Field on record to use as the cursor"
                />
                <ToggleGroupField<RequestOption>
                  label="Slice request option"
                  tooltip="Optionally configures how the slice values will be sent in requests to the source API"
                  fieldPath={streamFieldPath("streamSlicer.request_option")}
                  initialValues={{
                    inject_into: "request_parameter",
                    type: "RequestOption",
                    field_name: "",
                  }}
                >
                  <InjectRequestOptionFields
                    path={streamFieldPath("streamSlicer.request_option")}
                    descriptor="slice value"
                    excludeInjectIntoValues={["path"]}
                  />
                </ToggleGroupField>
              </>
            ),
          },
          {
            label: "Datetime",
            typeValue: "DatetimeStreamSlicer",
            children: (
              <>
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.datetime_format")}
                  label="Datetime format"
                  tooltip="Specify the format of the start and end time, e.g. %Y-%m-%d"
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.start_datetime")}
                  label="Start datetime"
                  tooltip="Start time to start slicing"
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.end_datetime")}
                  label="End datetime"
                  tooltip="End time to end slicing"
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.step")}
                  label="Step"
                  tooltip="Time interval for which to break up stream into slices, e.g. 1d"
                  pattern={timeDeltaRegex}
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.cursor_field")}
                  label="Cursor field"
                  tooltip="Field on record to use as the cursor"
                />
                <BuilderOptional>
                  <BuilderField
                    type="string"
                    path={streamFieldPath("streamSlicer.lookback_window")}
                    label="Lookback window"
                    tooltip="How many days before the start_datetime to read data for, e.g. 31d"
                    optional
                  />
                  <ToggleGroupField<RequestOption>
                    label="Start time request option"
                    tooltip="Optionally configures how the start datetime will be sent in requests to the source API"
                    fieldPath={streamFieldPath("streamSlicer.start_time_option")}
                    initialValues={{
                      inject_into: "request_parameter",
                      type: "RequestOption",
                      field_name: "",
                    }}
                  >
                    <InjectRequestOptionFields
                      path={streamFieldPath("streamSlicer.start_time_option")}
                      descriptor="start datetime"
                      excludeInjectIntoValues={["path"]}
                    />
                  </ToggleGroupField>
                  <ToggleGroupField<RequestOption>
                    label="End time request option"
                    tooltip="Optionally configures how the end datetime will be sent in requests to the source API"
                    fieldPath={streamFieldPath("streamSlicer.end_time_option")}
                    initialValues={{
                      inject_into: "request_parameter",
                      type: "RequestOption",
                      field_name: "",
                    }}
                  >
                    <InjectRequestOptionFields
                      path={streamFieldPath("streamSlicer.end_time_option")}
                      descriptor="end datetime"
                      excludeInjectIntoValues={["path"]}
                    />
                  </ToggleGroupField>
                  <BuilderField
                    type="string"
                    path={streamFieldPath("streamSlicer.stream_state_field_start")}
                    label="Stream state field start"
                    tooltip="Set which field on the stream state to use to determine the starting point"
                    optional
                  />
                  <BuilderField
                    type="string"
                    path={streamFieldPath("streamSlicer.stream_state_field_end")}
                    label="Stream state field end"
                    tooltip="Set which field on the stream state to use to determine the ending point"
                    optional
                  />
                </BuilderOptional>
              </>
            ),
          },
        ]}
      />
    </BuilderCard>
  );
};
