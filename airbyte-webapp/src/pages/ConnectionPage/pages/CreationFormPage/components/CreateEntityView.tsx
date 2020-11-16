import React, { useEffect, useState, useCallback } from "react";

import useRouter from "../../../../../components/hooks/useRouterHook";
import ContentCard from "../../../../../components/ContentCard";
import CheckConnection from "./CheckConnection";
import useSource from "../../../../../components/hooks/services/useSourceHook";
import { Routes } from "../../../../routes";
import useDestination from "../../../../../components/hooks/services/useDestinationHook";

type IProps = {
  type: "source" | "destination";
  afterSuccess: () => void;
};

const CreateEntityView: React.FC<IProps> = ({ type, afterSuccess }) => {
  const { location }: { location: any } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);

  const { checkSourceConnection } = useSource();
  const { checkDestinationConnection } = useDestination();

  const checkConnectionRequest = useCallback(async () => {
    try {
      setErrorStatusRequest(0);
      setSuccessRequest(false);

      if (type === "source") {
        await checkSourceConnection({
          sourceId: `${location.state?.sourceId}`
        });
      } else {
        await checkDestinationConnection({
          destinationId: `${location.state?.destinationId}`
        });
      }

      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        afterSuccess();
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type]);

  useEffect(() => {
    (async () => {
      if (location.state) {
        await checkConnectionRequest();
      }
    })();
  }, [checkConnectionRequest, checkSourceConnection, location.state, type]);

  if (errorStatusRequest) {
    const link =
      type === "source"
        ? `${Routes.Source}/${location.state?.sourceId}`
        : `${Routes.Destination}/${location.state?.destinationId}`;

    return (
      <ContentCard>
        <CheckConnection
          success={false}
          type={type}
          error={errorStatusRequest}
          retry={checkConnectionRequest}
          linkToSettings={link}
        />
      </ContentCard>
    );
  }

  return (
    <ContentCard>
      <CheckConnection
        isLoading={!successRequest}
        type={type}
        success={successRequest}
      />
    </ContentCard>
  );
};

export default CreateEntityView;
