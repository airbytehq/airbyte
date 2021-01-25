import React, { useEffect, useState } from "react";

import { FormattedMessage } from "react-intl";

import config from "../../../config";
import Link from "../../Link";

type IProps = {
  connector?: string;
};

const TIMEOUT_MS = 10000;

const ShowLoadingMessage: React.FC<IProps> = ({ connector }) => {
  const [longLoading, setLongLoading] = useState(false);

  useEffect(() => {
    setLongLoading(false);
    const timer = setTimeout(() => {
      setLongLoading(true);
    }, TIMEOUT_MS);
    return () => {
      clearTimeout(timer);
    };
  }, [connector]);

  return longLoading ? (
    <FormattedMessage
      id="form.tooLong"
      values={{
        lnk: (...lnk: React.ReactNode[]) => (
          <Link target="_blank" href={config.ui.technicalSupport} as="a">
            {lnk}
          </Link>
        )
      }}
    />
  ) : (
    <FormattedMessage id="form.loadingConfiguration" values={{ connector }} />
  );
};

export default ShowLoadingMessage;
