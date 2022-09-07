import React from "react";
import { FormattedMessage } from "react-intl";
import { components, ControlProps } from "react-select";
import styled from "styled-components";

import { DropDown, DropdownProps } from "components";
import { IDataItem, OptionView } from "components/base/DropDown/components/Option";
import { IProps } from "components/base/DropDown/components/SingleValue";
import Text from "components/base/DropDown/components/Text";

const ValueView = styled(components.SingleValue)`
  display: flex;
  align-items: center;
  overflow: visible !important;
  text-overflow: initial !important;
  word-break: normal;
  white-space: normal !important;
  line-height: 12px;
  font-size: 11px;
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
  font-size: 12px;
`;

const DropdownControl = styled(components.Control)<ControlProps<IDataItem, false>>`
  &.react-select__control {
    // background: ${({ theme }) => theme.greyColor20};
    // TODO: fix theme
    background: #e8e8ed;
    border-color: #e8e8ed;
    min-height: 30px;
    max-height: 30px;
  }
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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Option: React.FC<any> = (props) => {
  const { syncMode, destinationSyncMode } = props.value;

  return (
    <components.Option {...props}>
      <OptionContent data-id={props.data.value} isSelected={props.isSelected && !props.isMulti}>
        <Mode
          title={<FormattedMessage id="connectionForm.syncType.source" />}
          label={<FormattedMessage id={`syncMode.${syncMode}`} />}
          separator="|"
        />
        <Mode
          title={<FormattedMessage id="connectionForm.syncType.destination" />}
          label={<FormattedMessage id={`destinationSyncMode.${destinationSyncMode}`} />}
        />
      </OptionContent>
    </components.Option>
  );
};

const SyncSettingsDropdown: React.FC<DropdownProps> = (props) => (
  <DropDown
    {...props}
    components={{
      SingleValue,
      Option,
      Control: DropdownControl,
    }}
    data-testid="syncSettingsDropdown"
    $withBorder
  />
);

export { SyncSettingsDropdown };
