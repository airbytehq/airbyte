import React from 'react';

import CreateConnectionContent from '@app/components/CreateConnectionContent';
import { Source } from '@app/core/resources/Source';
import { Destination } from '@app/core/resources/Destination';
import { Routes } from '../../routes';
import useRouter from '@app/hooks/useRouter';
import SkipOnboardingButton from './SkipOnboardingButton';

type IProps = {
  errorStatus?: number;
  source: Source;
  destination: Destination;
};

const ConnectionStep: React.FC<IProps> = ({ source, destination }) => {
  const { push } = useRouter();

  const afterSubmitConnection = () => push(Routes.Root);

  return (
    <CreateConnectionContent
      additionBottomControls={<SkipOnboardingButton step="connection" />}
      source={source}
      destination={destination}
      afterSubmitConnection={afterSubmitConnection}
    />
  );
};

export default ConnectionStep;
