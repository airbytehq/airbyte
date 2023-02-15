import { useField } from "formik";
import capitalize from "lodash/capitalize";
import { useIntl } from "react-intl";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";

import { RequestOption } from "core/request/ConnectorManifest";

import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderFieldWithInputs } from "./BuilderFieldWithInputs";
import { BuilderOneOf } from "./BuilderOneOf";
import { InjectRequestOptionFields } from "./InjectRequestOptionFields";
import { ToggleGroupField } from "./ToggleGroupField";
import { BuilderPaginator } from "../types";

interface PaginationSectionProps {
  streamFieldPath: (fieldPath: string) => string;
  currentStreamIndex: number;
}

export const PaginationSection: React.FC<PaginationSectionProps> = ({ streamFieldPath, currentStreamIndex }) => {
  const { formatMessage } = useIntl();
  const [field, , helpers] = useField<BuilderPaginator | undefined>(streamFieldPath("paginator"));
  const [pageSizeField] = useField(streamFieldPath("paginator.strategy.page_size"));
  const [, , pageSizeOptionHelpers] = useField(streamFieldPath("paginator.pageSizeOption"));

  const handleToggle = (newToggleValue: boolean) => {
    if (newToggleValue) {
      helpers.setValue({
        strategy: {
          type: "OffsetIncrement",
          page_size: "",
        },
        pageTokenOption: {
          type: "RequestOption",
          inject_into: "request_parameter",
        },
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
            label="Pagination"
            infoTooltipContent="Configure how pagination is handled by your connector"
          />
        ),
        toggledOn,
        onToggle: handleToggle,
      }}
      copyConfig={{
        path: "paginator",
        currentStreamIndex,
        copyFromLabel: formatMessage({ id: "connectorBuilder.copyFromPaginationTitle" }),
        copyToLabel: formatMessage({ id: "connectorBuilder.copyToPaginationTitle" }),
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
                  label="Limit"
                  tooltip="Set the limit of each page"
                />
                <PageSizeOption label="limit" streamFieldPath={streamFieldPath} />
                <PageTokenOption label="offset" streamFieldPath={streamFieldPath} />
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
                <PageSizeOption label="page size" streamFieldPath={streamFieldPath} />
                <PageTokenOption label="page number" streamFieldPath={streamFieldPath} />
              </>
            ),
          },
          {
            label: "Cursor Pagination",
            typeValue: "CursorPagination",
            children: (
              <>
                <BuilderFieldWithInputs
                  type="string"
                  path={streamFieldPath("paginator.strategy.cursor_value")}
                  label="Cursor value"
                  tooltip="Value of the cursor to send in requests to the API"
                />
                <BuilderFieldWithInputs
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
                {pageSizeField.value && pageSizeField.value !== "" && (
                  <PageSizeOption label="page size" streamFieldPath={streamFieldPath} />
                )}
                <PageTokenOption label="cursor value" streamFieldPath={streamFieldPath} />
              </>
            ),
          },
        ]}
      />
    </BuilderCard>
  );
};

const PageTokenOption = ({
  label,
  streamFieldPath,
}: {
  label: string;
  streamFieldPath: (fieldPath: string) => string;
}): JSX.Element => {
  return (
    <GroupControls
      label={
        <ControlLabels
          label={`${capitalize(label)} request option`}
          infoTooltipContent={`Configures how the ${label} will be sent in requests to the source API`}
        />
      }
    >
      <InjectRequestOptionFields path={streamFieldPath("paginator.pageTokenOption")} descriptor={label} />
    </GroupControls>
  );
};

const PageSizeOption = ({
  label,
  streamFieldPath,
}: {
  label: string;
  streamFieldPath: (fieldPath: string) => string;
}): JSX.Element => {
  return (
    <ToggleGroupField<RequestOption>
      label={`${capitalize(label)} request option`}
      tooltip={`Configures how the ${label} will be sent in requests to the source API`}
      fieldPath={streamFieldPath("paginator.pageSizeOption")}
      initialValues={{
        inject_into: "request_parameter",
        type: "RequestOption",
        field_name: "",
      }}
    >
      <InjectRequestOptionFields
        path={streamFieldPath("paginator.pageSizeOption")}
        descriptor={label}
        excludeInjectIntoValues={["path"]}
      />
    </ToggleGroupField>
  );
};
