import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DropDown, DropDownRow } from "components";

import { LOCALES } from "locales";

interface IProps {
  labelId?: string;
  value?: string;
  onChange?: (language: DropDownRow.IDataItem) => void;
}

const DDLabel = styled.div`
  font-style: normal;
  font-weight: 500;
  font-size: 13px;
  line-height: 20px;
  color: #374151;
`;

export const LanguageDropdown: React.FC<IProps> = ({ labelId, value, onChange }) => {
  const languages: DropDownRow.IDataItem[] = [
    { label: "English", value: LOCALES.ENGLISH },
    { label: "简体中文", value: LOCALES.CHINESE_SIMPLIFIED },
  ];

  return (
    <>
      {labelId && (
        <DDLabel>
          <FormattedMessage id={labelId} />
        </DDLabel>
      )}
      <DropDown
        $withBorder
        $background="white"
        options={languages}
        value={value}
        onChange={(option: DropDownRow.IDataItem) => onChange?.(option)}
      />
    </>
  );
};
