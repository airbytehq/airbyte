import React from "react";
import { FormattedMessage } from "react-intl";

import PageTitle from "components/PageTitle";
import { Button } from "components/base";
//
// const CreditsLink = styled(Link)`
//   margin-left: 10px;
//   font-size: 11px;
//   line-height: 21px;
// `;

const CreditsTitle: React.FC = () => {
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
        <Button disabled>
          <FormattedMessage id="credits.buyCredits" />
        </Button>
      }
    />
  );
};

export default CreditsTitle;
