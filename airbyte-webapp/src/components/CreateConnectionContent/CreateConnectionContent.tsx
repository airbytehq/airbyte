import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, ContentCard } from "components";
import { IDataItem } from "components/base/DropDown/components/Option";
import JobItem from "components/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { Connection } from "core/domain/connection";
import { Destination, Source } from "core/domain/connector";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useCreateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import ConnectionForm from "views/Connection/ConnectionForm";

import { useDiscoverSchema } from "../../hooks/services/useSourceHook";
import TryAfterErrorBlock from "./components/TryAfterErrorBlock";

const SkipButton = styled.div`
  margin-top: 6px;

  & > button {
    min-width: 239px;
    margin-left: 9px;
  }
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin: 0 10px -1px 0;
  font-size: 14px;
`;

type IProps = {
  additionBottomControls?: React.ReactNode;
  source: Source;
  destination: Destination;
  afterSubmitConnection?: (connection: Connection) => void;
  noTitles?: boolean;
};

const CreateConnectionContent: React.FC<IProps> = ({
  source,
  destination,
  afterSubmitConnection,
  additionBottomControls,
  noTitles,
}) => {
  const { mutateAsync: createConnection } = useCreateConnection();
  const analyticsService = useAnalyticsService();

  const { schema, isLoading, schemaErrorStatus, catalogId, onDiscoverSchema } = useDiscoverSchema(source.sourceId);

  const connection = useMemo(
    () => ({
      syncCatalog: schema,
      destination,
      source,
      catalogId,
    }),
    [schema, destination, source, catalogId]
  );

  const onSubmitConnectionStep = async (values: ValuesProps) => {
    const connection = await createConnection({
      values,
      source: source,
      destination: destination,
      sourceDefinition: {
        name: source?.name ?? "",
        sourceDefinitionId: source?.sourceDefinitionId ?? "",
      },
      destinationDefinition: {
        name: destination?.name ?? "",
        destinationDefinitionId: destination?.destinationDefinitionId ?? "",
      },
      sourceCatalogId: catalogId,
    });

    return {
      onSubmitComplete: () => {
        afterSubmitConnection?.(connection);
      },
    };
  };

  const onSelectFrequency = (item: IDataItem | null) => {
    analyticsService.track("New Connection - Action", {
      action: "Select a frequency",
      frequency: item?.label,
      connector_source_definition: source?.sourceName,
      connector_source_definition_id: source?.sourceDefinitionId,
      connector_destination_definition: destination?.destinationName,
      connector_destination_definition_id: destination?.destinationDefinitionId,
    });
  };

  if (schemaErrorStatus) {
    const jobInfo = LogsRequestError.extractJobInfo(schemaErrorStatus);
    return (
      <ContentCard title={noTitles ? null : <FormattedMessage id="onboarding.setConnection" />}>
        <TryAfterErrorBlock
          onClick={onDiscoverSchema}
          additionControl={<SkipButton>{additionBottomControls}</SkipButton>}
        />
        {jobInfo && <JobItem jobInfo={jobInfo} />}
      </ContentCard>
    );
  }

  return (
    <ContentCard title={noTitles ? null : <FormattedMessage id="onboarding.setConnection" />}>
      {isLoading ? (
        <LoadingSchema />
      ) : (
        <Suspense fallback={<LoadingSchema />}>
          <ConnectionForm
            connection={connection}
            additionBottomControls={additionBottomControls}
            onDropDownSelect={onSelectFrequency}
            additionalSchemaControl={
              <Button onClick={onDiscoverSchema} type="button">
                <TryArrow icon={faRedoAlt} />
                <FormattedMessage id="connection.refreshSchema" />
              </Button>
            }
            onSubmit={onSubmitConnectionStep}
          />
        </Suspense>
      )}
    </ContentCard>
  );
};

export default CreateConnectionContent;
