import React from "react";
import { FormattedMessage } from "react-intl";

import { Cell, Header } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { Text } from "components/ui/Text";
import { InfoTooltip, TooltipLearnMoreLink } from "components/ui/Tooltip";

import { useBulkEditService } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { links } from "utils/links";

import styles from "./CatalogTreeTableHeader.module.scss";

const TextCell: React.FC<React.PropsWithChildren<{ flex?: number }>> = ({ flex, children }) => {
  return (
    <Cell flex={flex}>
      <Text size="sm" className={styles.cellText}>
        {children}
      </Text>
    </Cell>
  );
};

export const CatalogTreeTableHeader: React.FC = () => {
  const { mode } = useConnectionFormService();
  const { onCheckAll, selectedBatchNodeIds, allChecked } = useBulkEditService();

  return (
    <Header className={styles.headerContainer}>
      <Cell className={styles.checkboxCell}>
        {mode !== "readonly" && (
          <CheckBox
            onChange={onCheckAll}
            indeterminate={selectedBatchNodeIds.length > 0 && !allChecked}
            checked={allChecked}
          />
        )}
      </Cell>
      <TextCell flex={0.4}>
        <FormattedMessage id="sources.sync" />
      </TextCell>
      {/* <TextCell>
        <FormattedMessage id="form.fields" />
      </TextCell> */}
      <TextCell>
        <FormattedMessage id="form.namespace" />
      </TextCell>
      <TextCell>
        <FormattedMessage id="form.streamName" />
      </TextCell>
      <TextCell>
        <FormattedMessage id="form.syncMode" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <TooltipLearnMoreLink url={links.syncModeLink} />
        </InfoTooltip>
      </TextCell>
      <TextCell>
        <FormattedMessage id="form.cursorField" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.cursor.info" />
        </InfoTooltip>
      </TextCell>
      <TextCell>
        <FormattedMessage id="form.primaryKey" />
      </TextCell>
      <Cell />
      <TextCell>
        <FormattedMessage id="form.namespace" />
      </TextCell>
      <TextCell>
        <FormattedMessage id="form.streamName" />
      </TextCell>
      <TextCell>
        <FormattedMessage id="form.syncMode" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <TooltipLearnMoreLink url={links.syncModeLink} />
        </InfoTooltip>
      </TextCell>
    </Header>
  );
};
