import { FormattedMessage } from "react-intl";

import { DiffVerb } from "../types";

export type DiffType = "field" | "stream";

interface DiffHeaderProps {
  diffCount: number;
  diffVerb: DiffVerb;
  diffType: DiffType;
}

export const DiffHeader: React.FC<DiffHeaderProps> = ({ diffCount, diffVerb, diffType }) => {
  return (
    <div>
      <FormattedMessage
        id={`connection.updateSchema.${diffVerb}`}
        values={{
          value: diffCount,
          item: <FormattedMessage id={`connection.updateSchema.${diffType}`} values={{ count: diffCount }} />,
        }}
      />
    </div>
  );
};
