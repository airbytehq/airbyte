import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage, useIntl } from "react-intl";
import { components, MenuListProps } from "react-select";

import { DropDown } from "components/ui/DropDown";

import { Geography } from "core/request/AirbyteClient";
import { links } from "utils/links";

import styles from "./DataGeographyDropdown.module.scss";

interface DataGeographyDropdownProps {
  geographies: Geography[];
  isDisabled?: boolean;
  onChange: (value: Geography) => void;
  value: Geography;
}

const CustomMenuList: React.FC<MenuListProps> = ({ children, ...rest }) => {
  return (
    <components.MenuList {...rest}>
      {children}
      <a href={links.dataResidencySurvey} target="_blank" rel="noreferrer" className={styles.requestLink}>
        <FontAwesomeIcon icon={faPlus} />
        <span className={styles.linkText}>
          <FormattedMessage id="connection.requestNewGeography" />
        </span>
      </a>
    </components.MenuList>
  );
};

export const DataGeographyDropdown: React.FC<DataGeographyDropdownProps> = ({
  geographies,
  isDisabled = false,
  onChange,
  value,
}) => {
  const { formatMessage } = useIntl();

  return (
    <DropDown
      isDisabled={isDisabled}
      options={geographies.map((geography) => ({
        label: formatMessage({
          id: `connection.geography.${geography}`,
          defaultMessage: geography.toUpperCase(),
        }),
        value: geography,
      }))}
      value={value}
      onChange={(option) => onChange(option.value)}
      components={{
        MenuList: CustomMenuList,
      }}
    />
  );
};
