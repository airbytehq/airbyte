import { Card } from "components/base";
import { JobItem } from "components/JobItem/JobItem";

import { SynchronousJobRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";

import TryAfterErrorBlock from "./TryAfterErrorBlock";

export const SchemaError = ({
  schemaErrorStatus,
  onDiscoverSchema,
}: {
  schemaErrorStatus: { status: number; response: SynchronousJobRead } | null;
  onDiscoverSchema: () => Promise<void>;
}) => {
  const job = LogsRequestError.extractJobInfo(schemaErrorStatus);
  return (
    <Card>
      <TryAfterErrorBlock onClick={onDiscoverSchema} />
      {job && <JobItem job={job} />}
    </Card>
  );
};
