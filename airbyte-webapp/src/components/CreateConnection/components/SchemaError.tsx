import { Card } from "components/base";
import { JobItem } from "components/JobItem/JobItem";

import { SynchronousJobRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import TryAfterErrorBlock from "./TryAfterErrorBlock";

export const SchemaError = ({
  schemaError,
}: {
  schemaError: { status: number; response: SynchronousJobRead } | null;
}) => {
  const job = LogsRequestError.extractJobInfo(schemaError);
  const { refreshSchema } = useConnectionFormService();
  return (
    <Card>
      <TryAfterErrorBlock onClick={refreshSchema} />
      {job && <JobItem job={job} />}
    </Card>
  );
};
