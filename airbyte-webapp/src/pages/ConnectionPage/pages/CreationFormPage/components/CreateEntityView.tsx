import React, { useEffect, useState, useCallback } from "react";

import useRouter from "hooks/useRouter";
import ContentCard from "components/ContentCard";
import CheckConnection from "./CheckConnection";
import useSource from "hooks/services/useSourceHook";
import { Routes } from "../../../../routes";
import useDestination from "hooks/services/useDestinationHook";
import { JobsLogItem } from "components/JobItem";
import { JobInfo } from "core/resources/Scheduler";

type IProps = {
  type: "source" | "destination";
  afterSuccess: () => void;
};

const CreateEntityView: React.FC<IProps> = ({ type, afterSuccess }) => {
  const { location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    status: number;
    response: JobInfo;
  } | null>(null);

  const { checkSourceConnection } = useSource();
  const { checkDestinationConnection } = useDestination();

  const checkConnectionRequest = useCallback(async () => {
    try {
      setErrorStatusRequest(null);
      setSuccessRequest(false);

      if (type === "source") {
        await checkSourceConnection({
          sourceId: `${location.state?.sourceId}`,
        });
      } else {
        await checkDestinationConnection({
          destinationId: `${location.state?.destinationId}`,
        });
      }

      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        afterSuccess();
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e);
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
          error={errorStatusRequest?.status}
          retry={checkConnectionRequest}
          linkToSettings={link}
        />
        <JobsLogItem jobInfo={errorStatusRequest?.response} />
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
