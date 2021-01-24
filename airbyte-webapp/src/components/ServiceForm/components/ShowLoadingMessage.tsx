import React, { useEffect, useState } from "react";

import { FormattedMessage } from "react-intl";

import config from "../../../config";
import Link from "../../Link";

type IProps = {
  connector?: string;
};

const ShowLoadingMessage: React.FC<IProps> = ({ connector }) => {
  const [longLoading, setLongLoading] = useState(false);

  useEffect(() => {
    setLongLoading(false);
    const timer = setTimeout(() => {
      setLongLoading(true);
    }, 10000);
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
