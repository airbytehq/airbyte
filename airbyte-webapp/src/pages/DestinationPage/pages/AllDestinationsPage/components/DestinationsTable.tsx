import React from 'react'
import { useResource } from 'rest-hooks'

import { ImplementationTable } from '@app/components/EntityTable'
import { Routes } from '@app/pages/routes'
import useRouter from '@app/hooks/useRouter'
import ConnectionResource from '@app/core/resources/Connection'
import { Destination } from '@app/core/resources/Destination'
import { getEntityTableData } from '@app/components/EntityTable/utils'
import { EntityTableDataItem } from '@app/components/EntityTable/types'
import DestinationDefinitionResource from '@app/core/resources/DestinationDefinition'
import useWorkspace from '@app/hooks/services/useWorkspace'

type IProps = {
    destinations: Destination[]
}

const DestinationsTable: React.FC<IProps> = ({ destinations }) => {
    const { push } = useRouter()
    const { workspace } = useWorkspace()
    const { connections } = useResource(ConnectionResource.listShape(), {
        workspaceId: workspace.workspaceId,
    })

    const { destinationDefinitions } = useResource(
        DestinationDefinitionResource.listShape(),
        {
            workspaceId: workspace.workspaceId,
        }
    )

    const data = getEntityTableData(
        destinations,
        connections,
        destinationDefinitions,
        'destination'
    )

    const clickRow = (destination: EntityTableDataItem) =>
        push(`${Routes.Destination}/${destination.entityId}`)

    return (
        <ImplementationTable
            data={data}
            onClickRow={clickRow}
            entity="destination"
        />
    )
}

export default DestinationsTable
