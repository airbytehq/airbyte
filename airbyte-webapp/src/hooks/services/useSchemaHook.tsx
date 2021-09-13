import { useEffect, useState, useCallback } from 'react'
import { useFetcher } from 'rest-hooks'

import { SyncSchema } from '@app/core/domain/catalog'
import SchemaResource from '@app/core/resources/Schema'
import { JobInfo } from '@app/core/resources/Scheduler'

export const useDiscoverSchema = (
    sourceId?: string
): {
    isLoading: boolean
    schema: SyncSchema
    schemaErrorStatus: { status: number; response: JobInfo } | null
    onDiscoverSchema: () => Promise<void>
} => {
    const [schema, setSchema] = useState<SyncSchema>({ streams: [] })
    const [isLoading, setIsLoading] = useState(false)
    const [schemaErrorStatus, setSchemaErrorStatus] = useState<{
        status: number
        response: JobInfo
    } | null>(null)

    const fetchDiscoverSchema = useFetcher(SchemaResource.schemaShape(), true)

    const onDiscoverSchema = useCallback(async () => {
        setIsLoading(true)
        setSchemaErrorStatus(null)
        try {
            const data = await fetchDiscoverSchema({ sourceId: sourceId || '' })
            setSchema(data.catalog)
        } catch (e) {
            setSchemaErrorStatus(e)
        } finally {
            setIsLoading(false)
        }
    }, [fetchDiscoverSchema, sourceId])

    useEffect(() => {
        ;(async () => {
            if (sourceId) {
                await onDiscoverSchema()
            }
        })()
    }, [fetchDiscoverSchema, onDiscoverSchema, sourceId])

    return { schemaErrorStatus, isLoading, schema, onDiscoverSchema }
}
