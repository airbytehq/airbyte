import React from "react";
import { Helmet } from "react-helmet-async";
import { useIntl } from "react-intl";

const AIRBYTE = "Airbyte";
const SEPARATOR = "|";

interface FormattedHeadTitle {
  id: string;
  values?: Record<string, string>;
}

interface StringHeadTitle {
  title: string;
}

type HeadTitleDefinition = FormattedHeadTitle | StringHeadTitle;

const isStringTitle = (v: HeadTitleDefinition): v is StringHeadTitle => {
  return "title" in v;
};

interface IProps {
  titles: HeadTitleDefinition[];
}

/**
 * Titles defined by {@link HeadTitleDefinition} will be
 * chained together with the {@link SEPARATOR}.
 */
export const HeadTitle: React.FC<IProps> = ({ titles }) => {
  const intl = useIntl();

  const getTitle = (d: HeadTitleDefinition): string => {
    return isStringTitle(d) ? d.title : intl.formatMessage({ id: d.id }, d.values);
  };

  const headTitle = titles.map(getTitle).join(` ${SEPARATOR} `);
  return (
    <Helmet titleTemplate={`${AIRBYTE} ${SEPARATOR} %s`} defaultTitle={AIRBYTE}>
      <title>{headTitle}</title>
    </Helmet>
  );
};
