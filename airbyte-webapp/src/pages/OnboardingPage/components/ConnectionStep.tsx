import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";
import styled from "styled-components";

import ContentCard from "../../../components/ContentCard";
import ConnectionBlock from "../../../components/ConnectionBlock";
import ConnectionForm from "./ConnectionForm";
import SourceResource, { Source } from "../../../core/resources/Source";
import DestinationResource from "../../../core/resources/Destination";
import Spinner from "../../../components/Spinner";
import { SyncSchema } from "../../../core/resources/Schema";

type IProps = {
  onSubmit: (values: {
    frequency: string;
    syncSchema: SyncSchema;
    source: Source;
  }) => void;
  currentSourceId: string;
  currentDestinationId: string;
  sourceImplementationId: string;
  errorStatus?: number;
};

const SpinnerBlock = styled.div`
  margin: 40px;
  text-align: center;
`;

const ConnectionStep: React.FC<IProps> = ({
  onSubmit,
  currentSourceId,
  currentDestinationId,
  errorStatus,
  sourceImplementationId
}) => {
  const currentSource = useResource(SourceResource.detailShape(), {
    sourceId: currentSourceId
  });
  const currentDestination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestinationId
  });

  const onSubmitStep = async (values: {
    frequency: string;
    syncSchema: SyncSchema;
  }) => {
    await onSubmit({
      ...values,
      source: {
        name: currentSource.name,
        sourceId: currentSource.sourceId
      }
    });
  };

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );
  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: currentSource.name }}
        itemTo={{ name: currentDestination.name }}
      />
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <Suspense
          fallback={
            <SpinnerBlock>
              <Spinner />
            </SpinnerBlock>
          }
        >
          <ConnectionForm
            onSubmit={onSubmitStep}
            errorMessage={errorMessage}
            sourceImplementationId={sourceImplementationId}
          />
        </Suspense>
      </ContentCard>
    </>
  );
};

export default ConnectionStep;
