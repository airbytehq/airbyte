import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import PageTitle from "components/PageTitle";
import { Button } from "components/base";
import Link from "components/Link";

const CreditsLink = styled(Link)`
  margin-left: 10px;
  font-size: 11px;
  line-height: 21px;
`;

const CreditsTitle: React.FC = () => {
  return (
    <PageTitle
      title={
        <>
          <FormattedMessage id="credits.credits" />
          <CreditsLink as="a" href="" $light>
            <FormattedMessage id="credits.whatAreCredits" />
          </CreditsLink>
        </>
      }
      endComponent={
        <Button>
          <FormattedMessage id="credits.buyCredits" />
        </Button>
      }
    />
  );
};

export default CreditsTitle;
