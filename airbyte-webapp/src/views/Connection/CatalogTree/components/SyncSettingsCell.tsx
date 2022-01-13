import React from "react";
import { components } from "react-select";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Cell } from "components/SimpleTableComponents";
import { DropDown, DropdownProps } from "components";
import Text from "components/base/DropDown/components/Text";
import { IProps } from "components/base/DropDown/components/SingleValue";
import { OptionView } from "components/base/DropDown/components/Option";

const ValueView = styled(components.SingleValue)`
  display: flex;
  align-items: center;
  overflow: visible !important;
  text-overflow: initial !important;
  word-break: normal;
  white-space: normal !important;
  line-height: 12px;
  padding-top: 2px;
`;

const Separator = styled.div`
  padding: 0 5px;
`;

const SingleValue: React.FC<IProps> = (props) => {
  const { syncMode, destinationSyncMode } = props.data.value;
  return (
    <Text>
      <ValueView {...props}>
        <div>
          <FormattedMessage id={`syncMode.${syncMode}`} />
        </div>
        <Separator>|</Separator>
        <div>
          <FormattedMessage id={`destinationSyncMode.${destinationSyncMode}`} />
        </div>
      </ValueView>
    </Text>
  );
};

const Title = styled.span`
  color: ${({ theme }) => theme.greyColor55};
  font-size: 10px;
  padding-right: 5px;
`;

const OptionContent = styled(OptionView)`
  justify-content: left;
`;

const Mode: React.FC<{
  title: React.ReactNode;
  label: React.ReactNode;
  separator?: string;
}> = (props) => {
  return (
    <>
      <Title> {props.title}:</Title>
      <div>{props.label}</div>
      {props.separator ? <Separator>{props.separator}</Separator> : null}
    </>
  );
};

const Option: React.FC<any> = (props) => {
  const { syncMode, destinationSyncMode } = props.value;

  return (
    <components.Option {...props}>
      <OptionContent
        data-id={props.data.value}
        isSelected={props.isSelected && !props.isMulti}
      >
        <Mode
          title={<FormattedMessage id="connectionForm.syncType.source" />}
          label={<FormattedMessage id={`syncMode.${syncMode}`} />}
          separator="|"
        />
        <Mode
          title={<FormattedMessage id="connectionForm.syncType.destination" />}
          label={
            <FormattedMessage
              id={`destinationSyncMode.${destinationSyncMode}`}
            />
          }
        />
      </OptionContent>
    </components.Option>
  );
};

const SyncSettingsDropdown: React.FC<DropdownProps> = (props) => (
  <DropDown
    {...props}
    components={{
      SingleValue: SingleValue,
      Option: Option,
    }}
    $withBorder
  />
);

const SyncSettingsCell: React.FC<DropdownProps> = (props) => (
  <Cell flex={1.5}>
    <SyncSettingsDropdown {...props} />
  </Cell>
);

export { SyncSettingsCell, SyncSettingsDropdown };
