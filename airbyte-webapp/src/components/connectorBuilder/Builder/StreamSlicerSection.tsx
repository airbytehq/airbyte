import { useField } from "formik";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";

import { injectIntoValues } from "../types";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderOneOf } from "./BuilderOneOf";
import { BuilderOptional } from "./BuilderOptional";

interface StreamSlicerSectionProps {
  streamFieldPath: (fieldPath: string) => string;
}

export const StreamSlicerSection: React.FC<StreamSlicerSectionProps> = ({ streamFieldPath }) => {
  const [field, , helpers] = useField(streamFieldPath("streamSlicer"));

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
                <BuilderField
                  type="enum"
                  path={streamFieldPath("streamSlicer.request_option.inject_into")}
                  options={injectIntoValues}
                  label="Inject into"
                  tooltip="Optionally inject a request option into a part of the HTTP request"
                  optional
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.request_option.field_name")}
                  label="Field name"
                  tooltip="Field name to use for request option set on the HTTP request"
                  optional
                />
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
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.cursor_field")}
                  label="Cursor field"
                  tooltip="Field on record to use as the cursor"
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("streamSlicer.datetime_format")}
                  label="Datetime format"
                  tooltip="Specify the format of the start and end time, e.g. %Y-%m-%d"
                />
                <BuilderOptional>
                  <BuilderField
                    type="string"
                    path={streamFieldPath("streamSlicer.lookback_window")}
                    label="Lookback window"
                    tooltip="How many days before the start_datetime to read data for, e.g. 31d"
                  />
                  <GroupControls
                    label={
                      <ControlLabels
                        label="Start time option"
                        infoTooltipContent="Optionally inject start time into the request for APIs that support time-based filtering"
                      />
                    }
                  >
                    <BuilderField
                      type="enum"
                      path={streamFieldPath("streamSlicer.start_time_option.inject_into")}
                      options={injectIntoValues}
                      label="Inject into"
                      tooltip="Configures where the start time should be set on the HTTP requests"
                      optional
                    />
                    <BuilderField
                      type="string"
                      path={streamFieldPath("streamSlicer.start_time_option.field_name")}
                      label="Field name"
                      tooltip="Configures which key should be used in the location that the start time is being injected into"
                      optional
                    />
                  </GroupControls>
                  <GroupControls
                    label={
                      <ControlLabels
                        label="End time option"
                        infoTooltipContent="Optionally inject end time into the request for APIs that support time-based filtering"
                      />
                    }
                  >
                    <BuilderField
                      type="enum"
                      path={streamFieldPath("streamSlicer.end_time_option.inject_into")}
                      options={injectIntoValues}
                      label="Inject into"
                      tooltip="Configures where the end time should be set on the HTTP requests"
                      optional
                    />
                    <BuilderField
                      type="string"
                      path={streamFieldPath("streamSlicer.end_time_option.field_name")}
                      label="Field name"
                      tooltip="Configures which key should be used in the location that the end time is being injected into"
                      optional
                    />
                  </GroupControls>
                </BuilderOptional>
              </>
            ),
          },
        ]}
      />
    </BuilderCard>
  );
};
