import React from "react";
import { FormattedMessage } from "react-intl";

import PageTitle from "components/PageTitle";
import { Button } from "components/base";
import { useIntercom } from "react-use-intercom";
//
// const CreditsLink = styled(Link)`
//   margin-left: 10px;
//   font-size: 11px;
//   line-height: 21px;
// `;

const CreditsTitle: React.FC = () => {
  const { show } = useIntercom();

  const handleGetCredits = () => {
    show();
  };

  return (
    <PageTitle
      title={
        <>
          <FormattedMessage id="credits.credits" />
          {/*<CreditsLink as="a" href="" $light>*/}
          {/*  <FormattedMessage id="credits.whatAreCredits" />*/}
          {/*</CreditsLink>*/}
        </>
      }
      endComponent={
        <Button onClick={handleGetCredits}>
          <FormattedMessage id="credits.buyCredits" />
        </Button>
      }
    />
  );
};

export default CreditsTitle;
