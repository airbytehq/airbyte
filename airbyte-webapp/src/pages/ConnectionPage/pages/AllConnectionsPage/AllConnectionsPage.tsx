import React, { Suspense } from 'react'
import { FormattedMessage } from 'react-intl'
import { useResource } from 'rest-hooks'

import {
    Button,
    MainPageWithScroll,
    PageTitle,
    LoadingPage,
} from '@app/components'
import ConnectionResource from '@app/core/resources/Connection'
import ConnectionsTable from './components/ConnectionsTable'
import { Routes } from '@app/pages/routes'
import useRouter from '@app/hooks/useRouter'
import HeadTitle from '@app/components/HeadTitle'
import Placeholder, { ResourceTypes } from '@app/components/Placeholder'
import useWorkspace from '@app/hooks/services/useWorkspace'

const AllConnectionsPage: React.FC = () => {
    const { push } = useRouter()
    const { workspace } = useWorkspace()
    const { connections } = useResource(ConnectionResource.listShape(), {
        workspaceId: workspace.workspaceId,
    })

    const onClick = () => push(`${Routes.Connections}${Routes.ConnectionNew}`)

    return (
        <MainPageWithScroll
            headTitle={<HeadTitle titles={[{ id: 'sidebar.connections' }]} />}
            pageTitle={
                <PageTitle
                    title={<FormattedMessage id="sidebar.connections" />}
                    endComponent={
                        <Button onClick={onClick}>
                            <FormattedMessage id="connection.newConnection" />
                        </Button>
                    }
                />
            }
        >
            <Suspense fallback={<LoadingPage />}>
                {connections.length ? (
                    <ConnectionsTable connections={connections} />
                ) : (
                    <Placeholder resource={ResourceTypes.Connections} />
                )}
            </Suspense>
        </MainPageWithScroll>
    )
}

export default AllConnectionsPage
