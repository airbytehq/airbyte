import { useEffect, useState, useCallback } from "react";
import { useFetcher } from "rest-hooks";

import SchemaResource, { SyncSchema } from "../../../core/resources/Schema";

export const useDiscoverSchema = (sourceId?: string) => {
  const [schema, setSchema] = useState<SyncSchema>({ streams: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [schemaErrorStatus, setSchemaErrorStatus] = useState(0);

  const fetchDiscoverSchema = useFetcher(SchemaResource.schemaShape(), true);

  const onDiscoverSchema = useCallback(async () => {
    setIsLoading(true);
    setSchemaErrorStatus(0);
    try {
      const data = await fetchDiscoverSchema({ sourceId: sourceId || "" });
      setSchema(data.schema);
    } catch (e) {
      setSchemaErrorStatus(e.status);
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
