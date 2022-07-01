import { FormattedMessage } from "react-intl";

export type DiffVerb = "new" | "removed" | "changed";

export type DiffType = "field" | "stream";

interface DiffHeaderProps {
  diffCount: number;
  diffVerb: DiffVerb;
  diffType: DiffType;
}

export const DiffHeader: React.FC<DiffHeaderProps> = ({ diffCount, diffVerb, diffType }) => {
  return (
    <div>
      {diffCount}{" "}
      <FormattedMessage
        id={`connection.updateSchema.${diffVerb}`}
        values={{
          item: <FormattedMessage id={`connection.updateSchema.${diffType}`} values={{ count: diffCount }} />,
        }}
      />
    </div>
  );
};
