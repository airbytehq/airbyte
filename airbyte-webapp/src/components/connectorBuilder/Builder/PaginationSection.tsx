import { useField } from "formik";

import { ControlLabels } from "components/LabeledControl";

import { injectIntoValues } from "../types";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderOneOf } from "./BuilderOneOf";
import { ToggleGroupField } from "./ToggleGroupField";

interface PaginationSectionProps {
  streamFieldPath: (fieldPath: string) => string;
}

export const PaginationSection: React.FC<PaginationSectionProps> = ({ streamFieldPath }) => {
  const [field, , helpers] = useField(streamFieldPath("paginator"));

  const handleToggle = (newToggleValue: boolean) => {
    if (newToggleValue) {
      helpers.setValue({
        strategy: {
          type: "OffsetIncrement",
        },
      });
    } else {
      helpers.setValue(undefined);
    }
  };
  const toggledOn = field.value !== undefined;

  const pageTokenOption = (
    <ToggleGroupField
      label="Page token option"
      tooltip="Configures how the page token will be sent in requests to the source API"
      fieldPath={streamFieldPath("paginator.pageTokenOption")}
      initialValues={{
        inject_into: "request_parameter",
        field_name: "",
      }}
    >
      <BuilderField
        type="enum"
        path={streamFieldPath("paginator.pageTokenOption.inject_into")}
        options={injectIntoValues}
        label="Inject into"
        tooltip="Configures where the page token should be set on the HTTP requests"
      />
      <BuilderField
        type="string"
        path={streamFieldPath("paginator.pageTokenOption.field_name")}
        label="Field name"
        tooltip="Configures which key should be used in the location that the page token is being injected into"
        optional
      />
    </ToggleGroupField>
  );

  // const pageTokenOption = (
  //   <GroupControls
  //     label={
  //       <ControlLabels
  //         label="Page token option"
  //         infoTooltipContent="Configures how the page token will be sent in requests to the source API"
  //       />
  //     }
  //   >
  //     <BuilderField
  //       type="enum"
  //       path={streamFieldPath("paginator.pageTokenOption.inject_into")}
  //       options={injectIntoValues}
  //       label="Inject into"
  //       tooltip="Configures where the page token should be set on the HTTP requests"
  //     />
  //     <BuilderField
  //       type="string"
  //       path={streamFieldPath("paginator.pageTokenOption.field_name")}
  //       label="Field name"
  //       tooltip="Configures which key should be used in the location that the page token is being injected into"
  //       optional
  //     />
  //   </GroupControls>
  // );

  // const pageSizeOption = (
  //   <GroupControls
  //     label={
  //       <ControlLabels
  //         label="Page size option"
  //         infoTooltipContent="Configures how the page size will be sent in requests to the source API"
  //       />
  //     }
  //   >
  //     <BuilderField
  //       type="enum"
  //       path={streamFieldPath("paginator.pageSizeOption.inject_into")}
  //       options={injectIntoValues}
  //       label="Inject into"
  //       tooltip="Configures where the page size should be set on the HTTP requests"
  //     />
  //     <BuilderField
  //       type="string"
  //       path={streamFieldPath("paginator.pageSizeOption.field_name")}
  //       label="Field name"
  //       tooltip="Configures which key should be used in the location that the page size is being injected into"
  //       optional
  //     />
  //   </GroupControls>
  // );

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
                  tooltip="Size of pages to request from API"
                />
                {pageTokenOption}
                {/* {pageSizeOption} */}
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
                  tooltip="Size of pages to request from API"
                />
                <BuilderField
                  type="number"
                  path={streamFieldPath("paginator.strategy.start_from_page")}
                  label="Start from page"
                  tooltip="Page number to start requesting pages from"
                  optional
                />
                {pageTokenOption}
                {/* {pageSizeOption} */}
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
                  type="number"
                  path={streamFieldPath("paginator.strategy.page_size")}
                  label="Page size"
                  tooltip="Size of pages to request from API"
                  optional
                />
                <BuilderField
                  type="number"
                  path={streamFieldPath("paginator.strategy.stop_condition")}
                  label="Stop condition"
                  tooltip="Condition that determines when to stop requesting further pages"
                  optional
                />
                {pageTokenOption}
                {/* {pageSizeOption} */}
              </>
            ),
          },
        ]}
      />
    </BuilderCard>
  );
};
