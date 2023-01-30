import { useField } from "formik";
import { useIntl } from "react-intl";

import { ControlLabels } from "components/LabeledControl";

import { RequestOption, SimpleRetrieverStreamSlicer } from "core/request/ConnectorManifest";

import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderFieldWithInputs } from "./BuilderFieldWithInputs";
import { BuilderList } from "./BuilderList";
import { BuilderOneOf, OneOfOption } from "./BuilderOneOf";
import { BuilderOptional } from "./BuilderOptional";
import { InjectRequestOptionFields } from "./InjectRequestOptionFields";
import { StreamReferenceField } from "./StreamReferenceField";
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

  const getRegularSlicingOptions = (buildPath: (path: string) => string): OneOfOption[] => [
    {
      label: "List",
      typeValue: "ListStreamSlicer",
      default: {
        slice_values: [],
        cursor_field: "",
      },
      children: (
        <>
          <BuilderField
            type="array"
            path={buildPath("slice_values")}
            label="Slice values"
            tooltip="List of values to iterate over"
          />
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("cursor_field")}
            label="Cursor field"
            tooltip="Field on record to use as the cursor"
          />
          <ToggleGroupField<RequestOption>
            label="Slice request option"
            tooltip="Optionally configures how the slice values will be sent in requests to the source API"
            fieldPath={buildPath("request_option")}
            initialValues={{
              inject_into: "request_parameter",
              type: "RequestOption",
              field_name: "",
            }}
          >
            <InjectRequestOptionFields
              path={buildPath("request_option")}
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
      default: {
        datetime_format: "",
        start_datetime: "",
        end_datetime: "",
        step: "",
        cursor_field: "",
      },
      children: (
        <>
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("datetime_format")}
            label="Datetime format"
            tooltip="Specify the format of the start and end time, e.g. %Y-%m-%d"
          />
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("cursor_granularity")}
            label="Cursor granularity"
            tooltip="Smallest increment the datetime format has (ISO 8601 duration) that will be used to ensure that the start of a slice does not overlap with the end of the previous one, e.g. for %Y-%m-%d the granularity should be P1D, for %Y-%m-%dT%H:%M:%SZ the granularity should be PT1S"
          />
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("start_datetime")}
            label="Start datetime"
            tooltip="Start time to start slicing"
          />
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("end_datetime")}
            label="End datetime"
            tooltip="End time to end slicing"
          />
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("step")}
            label="Step"
            tooltip="Time interval (ISO 8601 duration) for which to break up stream into slices, e.g. P1D for daily slices"
          />
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("cursor_field")}
            label="Cursor field"
            tooltip="Field on record to use as the cursor"
          />
          <ToggleGroupField<RequestOption>
            label="Start time request option"
            tooltip="Optionally configures how the start datetime will be sent in requests to the source API"
            fieldPath={buildPath("start_time_option")}
            initialValues={{
              inject_into: "request_parameter",
              type: "RequestOption",
              field_name: "",
            }}
          >
            <InjectRequestOptionFields
              path={buildPath("start_time_option")}
              descriptor="start datetime"
              excludeInjectIntoValues={["path"]}
            />
          </ToggleGroupField>
          <ToggleGroupField<RequestOption>
            label="End time request option"
            tooltip="Optionally configures how the end datetime will be sent in requests to the source API"
            fieldPath={buildPath("end_time_option")}
            initialValues={{
              inject_into: "request_parameter",
              type: "RequestOption",
              field_name: "",
            }}
          >
            <InjectRequestOptionFields
              path={buildPath("end_time_option")}
              descriptor="end datetime"
              excludeInjectIntoValues={["path"]}
            />
          </ToggleGroupField>
          <BuilderOptional>
            <BuilderFieldWithInputs
              type="string"
              path={buildPath("lookback_window")}
              label="Lookback window"
              tooltip="Time interval (ISO 8601 duration) before the start_datetime to read data for, e.g. P1M for looking back one month"
              optional
            />
            <BuilderFieldWithInputs
              type="string"
              path={buildPath("stream_state_field_start")}
              label="Stream state field start"
              tooltip="Set which field on the stream state to use to determine the starting point"
              optional
            />
            <BuilderFieldWithInputs
              type="string"
              path={buildPath("stream_state_field_end")}
              label="Stream state field end"
              tooltip="Set which field on the stream state to use to determine the ending point"
              optional
            />
          </BuilderOptional>
        </>
      ),
    },
    {
      label: "Substream",
      typeValue: "SubstreamSlicer",
      default: {
        parent_key: "",
        stream_slice_field: "",
        parentStreamReference: "",
      },
      children: (
        <>
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("parent_key")}
            label="Parent key"
            tooltip="The key of the parent stream's records that will be the stream slice key"
          />
          <BuilderFieldWithInputs
            type="string"
            path={buildPath("stream_slice_field")}
            label="Stream slice field"
            tooltip="The name of the field on the stream_slice object that will be set to value of the Parent key"
          />
          <StreamReferenceField
            currentStreamIndex={currentStreamIndex}
            path={buildPath("parentStreamReference")}
            label="Parent stream"
            tooltip="The stream to read records from. Make sure there are no cyclic dependencies between streams"
          />
        </>
      ),
    },
  ];

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
          ...getRegularSlicingOptions((path: string) => streamFieldPath(`streamSlicer.${path}`)),
          {
            label: "Cartesian product",
            typeValue: "CartesianProductStreamSlicer",
            default: {
              stream_slicers: [],
            },
            children: (
              <BuilderList
                basePath={streamFieldPath("streamSlicer.stream_slicers")}
                emptyItem={{
                  type: "ListStreamSlicer",
                  slice_values: [],
                  cursor_field: "",
                }}
              >
                {({ buildPath }) => (
                  <BuilderOneOf
                    path={buildPath("")}
                    label="Sub slicer"
                    tooltip="Method to use on this sub slicer"
                    options={getRegularSlicingOptions(buildPath)}
                  />
                )}
              </BuilderList>
            ),
          },
        ]}
      />
    </BuilderCard>
  );
};
