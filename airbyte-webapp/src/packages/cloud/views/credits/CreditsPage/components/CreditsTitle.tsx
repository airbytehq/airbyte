import React from "react";
import { FormattedMessage } from "react-intl";
import { useIntercom } from "react-use-intercom";

import PageTitle from "components/PageTitle";
import { Button } from "components/base";

const CreditsTitle: React.FC = () => {
  const { show } = useIntercom();

  const handleGetCredits = () => {
    show();
  };

  return (
    <PageTitle
      title={<FormattedMessage id="credits.credits" />}
      endComponent={
        <Button onClick={handleGetCredits}>
          <FormattedMessage id="credits.buyCredits" />
        </Button>
      }
    />
  );
};

export default CreditsTitle;
