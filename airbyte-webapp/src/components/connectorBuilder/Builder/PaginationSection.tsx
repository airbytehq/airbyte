import { useField } from "formik";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";

import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderOneOf } from "./BuilderOneOf";
import { InjectRequestOptionFields } from "./InjectRequestOptionFields";
import { ToggleGroupField } from "./ToggleGroupField";

interface PaginationSectionProps {
  streamFieldPath: (fieldPath: string) => string;
}

export const PaginationSection: React.FC<PaginationSectionProps> = ({ streamFieldPath }) => {
  const [field, , helpers] = useField(streamFieldPath("paginator"));
  const [pageSizeField] = useField(streamFieldPath("paginator.strategy.page_size"));
  const [, , pageSizeOptionHelpers] = useField(streamFieldPath("paginator.pageSizeOption"));

  const handleToggle = (newToggleValue: boolean) => {
    if (newToggleValue) {
      helpers.setValue({
        strategy: {
          type: "OffsetIncrement",
        },
        pageTokenOption: {
          inject_into: "request_parameter",
        },
      });
    } else {
      helpers.setValue(undefined);
    }
  };
  const toggledOn = field.value !== undefined;

  const pageTokenOption = (
    <GroupControls
      label={
        <ControlLabels
          label="Page token option"
          infoTooltipContent="Configures how the page token will be sent in requests to the source API"
        />
      }
    >
      <InjectRequestOptionFields path={streamFieldPath("paginator.pageTokenOption")} descriptor="page token" />
    </GroupControls>
  );

  const pageSizeOption = (
    <ToggleGroupField
      label="Page size option"
      tooltip="Optionally configures how the page size will be sent in requests to the source API"
      fieldPath={streamFieldPath("paginator.pageSizeOption")}
      initialValues={{
        inject_into: "request_parameter",
        field_name: "",
      }}
    >
      <InjectRequestOptionFields
        path={streamFieldPath("paginator.pageSizeOption")}
        descriptor="page size"
        excludeInjectIntoValues={["path"]}
      />
    </ToggleGroupField>
  );

  return (
    <BuilderCard
      toggleConfig={{
        label: (
          <ControlLabels
            label="Pagination"
            infoTooltipContent="Configure how pagination is handled by your connector"
          />
        ),
        toggledOn,
        onToggle: handleToggle,
      }}
    >
      <BuilderOneOf
        path={streamFieldPath("paginator.strategy")}
        label="Mode"
        tooltip="Pagination method to use for requests sent to the API"
        options={[
          {
            label: "Offset Increment",
            typeValue: "OffsetIncrement",
            children: (
              <>
                <BuilderField
                  type="number"
                  path={streamFieldPath("paginator.strategy.page_size")}
                  label="Page size"
                  tooltip="Set the size of each page"
                />
                {pageSizeOption}
                {pageTokenOption}
              </>
            ),
          },
          {
            label: "Page Increment",
            typeValue: "PageIncrement",
            children: (
              <>
                <BuilderField
                  type="number"
                  path={streamFieldPath("paginator.strategy.page_size")}
                  label="Page size"
                  tooltip="Set the size of each page"
                />
                <BuilderField
                  type="number"
                  path={streamFieldPath("paginator.strategy.start_from_page")}
                  label="Start from page"
                  tooltip="Page number to start requesting pages from"
                  optional
                />
                {pageSizeOption}
                {pageTokenOption}
              </>
            ),
          },
          {
            label: "Cursor Pagination",
            typeValue: "CursorPagination",
            children: (
              <>
                <BuilderField
                  type="string"
                  path={streamFieldPath("paginator.strategy.cursor_value")}
                  label="Cursor value"
                  tooltip="Value of the cursor to send in requests to the API"
                />
                <BuilderField
                  type="string"
                  path={streamFieldPath("paginator.strategy.stop_condition")}
                  label="Stop condition"
                  tooltip="Condition that determines when to stop requesting further pages"
                  optional
                />
                <BuilderField
                  type="number"
                  path={streamFieldPath("paginator.strategy.page_size")}
                  onChange={(newValue) => {
                    if (newValue === undefined || newValue === "") {
                      pageSizeOptionHelpers.setValue(undefined);
                    }
                  }}
                  label="Page size"
                  tooltip="Set the size of each page"
                  optional
                />
                {pageSizeField.value && pageSizeField.value !== "" && pageSizeOption}
                {pageTokenOption}
              </>
            ),
          },
        ]}
      />
    </BuilderCard>
  );
};
