import { useIntl } from "react-intl";

import { DiffVerb } from "../types";

export type DiffType = "field" | "stream";

interface DiffHeaderProps {
  diffCount: number;
  diffVerb: DiffVerb;
  diffType: DiffType;
}

export const DiffHeader: React.FC<DiffHeaderProps> = ({ diffCount, diffVerb, diffType }) => {
  const { formatMessage } = useIntl();

  const text = formatMessage(
    {
      id: `connection.updateSchema.${diffVerb}`,
    },
    {
      value: diffCount,
      item: formatMessage({ id: `connection.updateSchema.${diffType}` }, { count: diffCount }),
    }
  );

  return <>{text}</>;
};
