import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";

import LoadingSchema from "./components/LoadingSchema";
import CreateConnection from "./components/CreateConnection";
import ContentCard from "../ContentCard";
import { IDataItem } from "../DropDown/components/ListItem";
import { AnalyticsService } from "../../core/analytics/AnalyticsService";
import config from "../../config";
import { Source } from "../../core/resources/Source";
import { Destination } from "../../core/resources/Destination";
import { SyncSchema } from "../../core/resources/Schema";
import useConnection from "../hooks/services/useConnectionHook";

type IProps = {
  source?: Source;
  destination?: Destination;
  afterSubmitConnection?: () => void;
};

const CreateConnectionContent: React.FC<IProps> = ({
  source,
  destination,
  afterSubmitConnection
}) => {
  const { createConnection } = useConnection();
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);

  const onSubmitConnectionStep = async (values: {
    frequency: string;
    syncSchema: SyncSchema;
  }) => {
    setErrorStatusRequest(0);
    try {
      await createConnection({
        values,
        source: source || undefined,
        destination: destination || undefined,
        sourceDefinition: {
          name: source?.name || "",
          sourceDefinitionId: source?.sourceDefinitionId || ""
        },
        destinationDefinition: {
          name: destination?.name || "",
          destinationDefinitionId: destination?.destinationDefinitionId || ""
        }
      });

      if (afterSubmitConnection) {
        afterSubmitConnection();
      }
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  const onSubmitStep = async (values: {
    frequency: string;
    syncSchema: SyncSchema;
  }) => {
    await onSubmitConnectionStep({
      ...values
    });
  };

  const onSelectFrequency = (item: IDataItem) => {
    AnalyticsService.track("New Connection - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a frequency",
      frequency: item?.text,
      connector_source_definition: source?.name,
      connector_source_definition_id: source?.sourceDefinitionId,
      connector_destination_definition: destination?.name,
      connector_destination_definition_id: destination?.destinationDefinitionId
    });
  };

  return (
    <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
      <Suspense fallback={<LoadingSchema />}>
        <CreateConnection
          sourceId={source?.sourceId || ""}
          onSelectFrequency={onSelectFrequency}
          onSubmit={onSubmitStep}
          errorStatus={errorStatusRequest}
        />
      </Suspense>
    </ContentCard>
  );
};

export default CreateConnectionContent;
