import { FormattedMessage } from "react-intl";

import { Cell, Header } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { InfoTooltip, TooltipLearnMoreLink } from "components/ui/Tooltip";

import { useBulkEditService } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { links } from "utils/links";

export const CatalogTreeTableHeader: React.FC = () => {
  const { mode } = useConnectionFormService();
  const { onCheckAll, selectedBatchNodeIds, allChecked } = useBulkEditService();

  return (
    <Header>
      <Cell>
        {mode !== "readonly" && (
          <CheckBox
            onChange={onCheckAll}
            indeterminate={selectedBatchNodeIds.length > 0 && !allChecked}
            checked={allChecked}
          />
        )}
      </Cell>
      <Cell>
        <FormattedMessage id="sources.sync" />
      </Cell>
      <Cell>
        <FormattedMessage id="form.fields" />
      </Cell>
      <Cell>
        <FormattedMessage id="form.namespace" />
      </Cell>
      <Cell>
        <FormattedMessage id="form.streamName" />
      </Cell>
      <Cell>
        <FormattedMessage id="form.syncMode" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <TooltipLearnMoreLink url={links.syncModeLink} />
        </InfoTooltip>
      </Cell>
      <Cell>
        <FormattedMessage id="form.cursorField" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.cursor.info" />
        </InfoTooltip>
      </Cell>
      <Cell>
        <FormattedMessage id="form.primaryKey" />
      </Cell>
      <Cell />
      <Cell>
        <FormattedMessage id="form.namespace" />
      </Cell>
      <Cell>
        <FormattedMessage id="form.streamName" />
      </Cell>
      <Cell>
        <FormattedMessage id="form.syncMode" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <TooltipLearnMoreLink url={links.syncModeLink} />
        </InfoTooltip>
      </Cell>
    </Header>
  );
};
