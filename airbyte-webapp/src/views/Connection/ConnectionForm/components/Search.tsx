import React from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";

import { Input } from "components";

interface SearchProps {
  onSearch: (value: string) => void;
}

const SearchInput = styled(Input)`
  padding: 10px 8px 9px;
`;

const SearchContent = styled.div`
  position: relative;
  width: 100%;

  &:before {
    content: attr(data-content);
  }
`;

const Search: React.FC<SearchProps> = ({ onSearch }) => {
  const { formatMessage } = useIntl();

  return (
    <SearchContent>
      <SearchInput
        placeholder={formatMessage({
          id: `form.nameSearch`,
        })}
        onChange={(e) => onSearch(e.target.value)}
      />
    </SearchContent>
  );
};

export default Search;
