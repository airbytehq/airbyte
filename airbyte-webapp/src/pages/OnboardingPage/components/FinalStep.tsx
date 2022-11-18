import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import { Heading } from "components/ui/Heading";

import Status from "core/statuses";
import { useOnboardingService } from "hooks/services/Onboarding/OnboardingService";
import { useConnectionList, useGetConnection, useSyncConnection } from "hooks/services/useConnectionHook";
import { links } from "utils/links";

import styles from "./FinalStep.module.scss";
import { FirstSuccessfulSync } from "./FirstSuccessfulSync";
import HighlightedText from "./HighlightedText";
import ProgressBlock from "./ProgressBlock";
import UseCaseBlock from "./UseCaseBlock";
import VideoItem from "./VideoItem";

const FinalStep: React.FC = () => {
  const { visibleUseCases, useCaseLinks, skipCase } = useOnboardingService();
  const { mutateAsync: syncConnection } = useSyncConnection();
  const { connections } = useConnectionList();
  const connection = useGetConnection(connections[0].connectionId, {
    refetchInterval: 2500,
  });
  const [isFirstSyncSuccessful, setIsFirstSyncSuccessful] = useState(false);

  useEffect(() => {
    if (connection.latestSyncJobStatus === Status.SUCCEEDED) {
      setIsFirstSyncSuccessful(true);
    }
  }, [connection.latestSyncJobStatus]);

  const onSync = () => syncConnection(connections[0]);

  return (
    <>
      <div className={styles.videos}>
        <VideoItem
          small
          description={<FormattedMessage id="onboarding.watchVideo" />}
          videoId="sKDviQrOAbU"
          img="/videoCover.png"
        />
        <VideoItem
          small
          description={<FormattedMessage id="onboarding.exploreDemo" />}
          link={links.demoLink}
          img="/videoCover.png"
        />
      </div>
      <ProgressBlock connection={connection} onSync={onSync} />
      {isFirstSyncSuccessful && <FirstSuccessfulSync />}
      <Heading as="h2" className={styles.title}>
        <FormattedMessage
          id="onboarding.useCases"
          values={{
            name: (name: React.ReactNode[]) => <HighlightedText>{name}</HighlightedText>,
          }}
        />
      </Heading>

      {visibleUseCases?.map((item, key) => (
        <UseCaseBlock key={item} count={key + 1} href={useCaseLinks[item]} onSkip={skipCase} id={item} />
      ))}
    </>
  );
};

export default FinalStep;
