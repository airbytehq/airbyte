import React from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch } from "@fortawesome/free-solid-svg-icons";

import { CheckBox, Input } from "components";

type SearchProps = {
  onCheckAll: () => void;
  onSearch: (value: string) => void;
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

const Search: React.FC<SearchProps> = ({
  onCheckAll,
  hasSelectedItem,
  onSearch,
}) => {
  const formatMessage = useIntl().formatMessage;

  return (
    <Content>
      <CheckBox onClick={onCheckAll} checked={hasSelectedItem} />
      <SearchContent>
        <SearchIcon icon={faSearch} />
        <SearchInput
          placeholder={formatMessage({
            id: `form.nameSearch`,
          })}
          onChange={(e) => onSearch(e.target.value)}
        />
      </SearchContent>
    </Content>
  );
};

export default Search;
