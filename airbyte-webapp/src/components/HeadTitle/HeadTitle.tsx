import React from "react";
import { Helmet } from "react-helmet";
import { FormattedMessage } from "react-intl";

type IProps = {
  titleId?: string;
  titleValues?: Record<string, string>;
};

const HeadTitle: React.FC<IProps> = ({ titleId, titleValues }) => (
  <FormattedMessage id={titleId} values={titleValues}>
    {(title) => (
      <Helmet titleTemplate="Airbyte | %s" defaultTitle="Airbyte">
        <title>{title}</title>
      </Helmet>
    )}
  </FormattedMessage>
);

export default HeadTitle;
