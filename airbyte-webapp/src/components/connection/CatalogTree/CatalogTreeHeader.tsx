import classnames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";

import { Cell, Header } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { InfoTooltip, TooltipLearnMoreLink } from "components/ui/Tooltip";

import { useBulkEditService } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { links } from "utils/links";

import styles from "./CatalogTreeHeader.module.scss";

export const CatalogTreeHeader: React.FC = () => {
  const { mode } = useConnectionFormService();
  const { onCheckAll, selectedBatchNodeIds, allChecked } = useBulkEditService();
  const catalogHeaderStyle = classnames({
    [styles.catalogHeader]: mode !== "readonly",
    [styles.readonlyCatalogHeader]: mode === "readonly",
  });

  return (
    <Header className={catalogHeaderStyle}>
      {mode !== "readonly" && (
        <Cell className={styles.checkboxCell}>
          <CheckBox
            onChange={onCheckAll}
            indeterminate={selectedBatchNodeIds.length > 0 && !allChecked}
            checked={allChecked}
          />
        </Cell>
      )}
      {mode !== "readonly" && <Cell flex={0.1} />}
      <Cell light flex={0.4}>
        <FormattedMessage id="sources.sync" />
      </Cell>
      <Cell light>
        <FormattedMessage id="sources.source" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.source.info" />
        </InfoTooltip>
      </Cell>
      <Cell />
      <Cell light flex={1.5}>
        <FormattedMessage id="form.syncMode" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <TooltipLearnMoreLink url={links.syncModeLink} />
        </InfoTooltip>
      </Cell>
      <Cell light>
        <FormattedMessage id="form.cursorField" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.cursor.info" />
        </InfoTooltip>
      </Cell>
      <Cell light>
        <FormattedMessage id="form.primaryKey" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.primaryKey.info" />
        </InfoTooltip>
      </Cell>
      <Cell light>
        <FormattedMessage id="connector.destination" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.destinationName.info" />
          <div className={styles.nextLineText}>
            <FormattedMessage id="connectionForm.destinationStream.info" />
          </div>
        </InfoTooltip>
      </Cell>
      <Cell />
    </Header>
  );
};
