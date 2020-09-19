import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";
import styled from "styled-components";

import ConnectionBlock from "../../../../../components/ConnectionBlock";
import ContentCard from "../../../../../components/ContentCard";
import { Destination } from "../../../../../core/resources/Destination";
import SourceResource from "../../../../../core/resources/Source";
import Spinner from "../../../../../components/Spinner";
import { SyncSchema } from "../../../../../core/resources/Schema";
import ConnectionForm from "./ConnectionForm";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  destination: Destination;
  sourceId: string;
  sourceImplementationId: string;
};

const SpinnerBlock = styled.div`
  margin: 40px;
  text-align: center;
`;

const CreateSourcePage: React.FC<IProps> = ({
  onSubmit,
  destination,
  sourceId,
  sourceImplementationId
}) => {
  const source = useResource(SourceResource.detailShape(), {
    sourceId
  });

  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: source.name }}
        itemTo={{ name: destination.name }}
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
            onSubmit={onSubmit}
            sourceImplementationId={sourceImplementationId}
          />
        </Suspense>
      </ContentCard>
    </>
  );
};

export default CreateSourcePage;
