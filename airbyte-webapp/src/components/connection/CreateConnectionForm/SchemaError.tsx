import { JobItem } from "components/JobItem/JobItem";
import { Card } from "components/ui/Card";

import { LogsRequestError } from "core/request/LogsRequestError";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { SchemaError as SchemaErrorType } from "hooks/services/useSourceHook";

import { TryAfterErrorBlock } from "./TryAfterErrorBlock";

export const SchemaError = ({ schemaError }: { schemaError: SchemaErrorType }) => {
  const job = LogsRequestError.extractJobInfo(schemaError);
  const { refreshSchema } = useConnectionFormService();
  return (
    <Card>
      <TryAfterErrorBlock onClick={refreshSchema} message={schemaError?.message} />
      {job && <JobItem job={job} />}
    </Card>
  );
};
