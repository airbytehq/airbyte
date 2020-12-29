import { useEffect, useState, useCallback } from "react";
import { useFetcher } from "rest-hooks";

import SchemaResource, { SyncSchema } from "../../../core/resources/Schema";
import { JobInfo } from "../../../core/resources/Scheduler";

export const useDiscoverSchema = (sourceId?: string) => {
  const [schema, setSchema] = useState<SyncSchema>({ streams: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [schemaErrorStatus, setSchemaErrorStatus] = useState<{
    status: number;
    response: JobInfo;
  } | null>(null);

  const fetchDiscoverSchema = useFetcher(SchemaResource.schemaShape(), true);

  const onDiscoverSchema = useCallback(async () => {
    setIsLoading(true);
    setSchemaErrorStatus(null);
    try {
      const data = await fetchDiscoverSchema({ sourceId: sourceId || "" });
      setSchema(data.schema);
    } catch (e) {
      setSchemaErrorStatus(e);
    } finally {
      setIsLoading(false);
    }
  }, [fetchDiscoverSchema, sourceId]);

  useEffect(() => {
    (async () => {
      if (sourceId) {
        await onDiscoverSchema();
      }
    })();
  }, [fetchDiscoverSchema, onDiscoverSchema, sourceId]);

  return { schemaErrorStatus, isLoading, schema, onDiscoverSchema };
};
