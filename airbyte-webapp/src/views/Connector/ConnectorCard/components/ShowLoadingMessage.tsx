import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import { ExternalLink } from "components/ui/Link";

import { links } from "utils/links";

interface ShowLoadingMessageProps {
  connector?: string;
}

const TIMEOUT_MS = 10000;

const ShowLoadingMessage: React.FC<ShowLoadingMessageProps> = ({ connector }) => {
  const [longLoading, setLongLoading] = useState(false);

  useEffect(() => {
    setLongLoading(false);
    const timer = setTimeout(() => setLongLoading(true), TIMEOUT_MS);
    return () => clearTimeout(timer);
  }, [connector]);

  return longLoading ? (
    <FormattedMessage
      id="form.tooLong"
      values={{
        lnk: (...lnk: React.ReactNode[]) => <ExternalLink href={links.technicalSupport}>{lnk}</ExternalLink>,
      }}
    />
  ) : (
    <FormattedMessage id="form.loadingConfiguration" values={{ connector }} />
  );
};

export default ShowLoadingMessage;
