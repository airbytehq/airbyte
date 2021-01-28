import React from "react";

import ConnectionBlock from "../../../components/ConnectionBlock";
import CreateConnectionContent from "../../../components/CreateConnectionContent";
import { Source } from "../../../core/resources/Source";
import { Destination } from "../../../core/resources/Destination";
import { Routes } from "../../routes";
import useRouter from "../../../components/hooks/useRouterHook";
import SkipOnboardingButton from "./SkipOnboardingButton";

type IProps = {
  errorStatus?: number;
  source?: Source;
  destination?: Destination;
};

const ConnectionStep: React.FC<IProps> = ({ source, destination }) => {
  const { push } = useRouter();

  const afterSubmitConnection = () => push(Routes.Root);

  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: source?.name || "" }}
        itemTo={{ name: destination?.name || "" }}
      />
      <CreateConnectionContent
        additionBottomControls={<SkipOnboardingButton step="connection" />}
        source={source}
        destination={destination}
        afterSubmitConnection={afterSubmitConnection}
      />
    </>
  );
};

export default ConnectionStep;
