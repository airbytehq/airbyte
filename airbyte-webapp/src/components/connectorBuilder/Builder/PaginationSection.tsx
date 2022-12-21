import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";

import { injectIntoValues } from "../types";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";

interface PaginationSectionProps {
  streamFieldPath: (fieldPath: string) => string;
}

export const PaginationSection: React.FC<PaginationSectionProps> = ({ streamFieldPath }) => {
  const pageTokenOption = (
    <GroupControls
      label={
        <ControlLabels
          label="Page token option"
          infoTooltipContent="Configures how the page token will be sent in requests to the source API"
        />
      }
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
    </GroupControls>
  );

  const pageSizeOption = (
    <GroupControls
      label={
        <ControlLabels
          label="Page size option"
          infoTooltipContent="Configures how the page size will be sent in requests to the source API"
        />
      }
    >
      <BuilderField
        type="enum"
        path={streamFieldPath("paginator.pageSizeOption.inject_into")}
        options={injectIntoValues}
        label="Inject into"
        tooltip="Configures where the page size should be set on the HTTP requests"
      />
      <BuilderField
        type="string"
        path={streamFieldPath("paginator.pageSizeOption.field_name")}
        label="Field name"
        tooltip="Configures which key should be used in the location that the page size is being injected into"
        optional
      />
    </GroupControls>
  );

  return (
    <BuilderCard>
      {pageTokenOption}
      {pageSizeOption}

      {/* <BuilderOneOf path={streamFieldPath("paginator.strategy")} label="Pagination" tooltip="Pagination method to use for requests sent to the API" options={[
          {label: ""}
        ]} /> */}
    </BuilderCard>
  );
};
