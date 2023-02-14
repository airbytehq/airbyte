import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DropDown, LoadingButton, DropDownRow } from "components";
import { Separator } from "components/Separator";

const PageContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
`;

const DDLabel = styled.div`
  font-style: normal;
  font-weight: 500;
  font-size: 13px;
  line-height: 20px;
  color: #374151;
`;

const ChangeBtnContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
`;

const LanguagePage: React.FC = () => {
  const languages: DropDownRow.IDataItem[] = [
    { label: "English", value: "English" },
    { label: "Chinese Simplified - 简体中文", value: "Chinese Simplified - 简体中文" },
  ];

  const [language, setLanguage] = useState<string>(languages[0].value);
  const [isUpdated, setIsUpdated] = useState<boolean>(false);

  return (
    <PageContainer>
      <DDLabel>
        <FormattedMessage id="settings.language.dropdownLabel" />
      </DDLabel>
      <DropDown
        $withBorder
        $background="white"
        options={languages}
        value={language}
        onChange={(option: DropDownRow.IDataItem) => {
          setLanguage((prevState) => {
            if (prevState !== option.value) {
              setIsUpdated(true);
            }
            return option.value;
          });
        }}
      />
      <Separator height="60px" />
      <ChangeBtnContainer>
        <LoadingButton size="lg" disabled={!isUpdated}>
          <FormattedMessage id="settings.language.btnText" />
        </LoadingButton>
      </ChangeBtnContainer>
    </PageContainer>
  );
};

export default LanguagePage;
