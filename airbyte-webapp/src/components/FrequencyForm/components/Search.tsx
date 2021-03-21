import React from "react";
// import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch } from "@fortawesome/free-solid-svg-icons";

import { CheckBox, Input } from "components";

type IProps = {
  onCheckAll: () => void;
  hasSelectedItem: boolean;
};

const Content = styled.div`
  padding-left: 30px;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const SearchInput = styled(Input)`
  padding: 3px 10px 3px 24px;
`;

const SearchIcon = styled(FontAwesomeIcon)`
  position: absolute;
  top: 6px;
  left: 6px;
  font-size: 14px;
  color: ${({ theme }) => theme.greyColor40};
`;

const SearchContent = styled.div`
  position: relative;
  margin-left: 10px;

  &:before {
    content: attr(data-content);
  }
`;

const Search: React.FC<IProps> = ({ onCheckAll, hasSelectedItem }) => {
  return (
    <Content>
      <CheckBox onClick={onCheckAll} checked={hasSelectedItem} />
      <SearchContent>
        <SearchIcon icon={faSearch} />
        <SearchInput />
      </SearchContent>
    </Content>
  );
};

export default Search;
