import React, { Suspense, useMemo, useState } from 'react'
import { FormattedMessage } from 'react-intl'
import { useResource } from 'rest-hooks'

import PageTitle from '@app/components/PageTitle'
import useRouter from '@app/hooks/useRouter'
import Placeholder, { ResourceTypes } from '@app/components/Placeholder'
import ConnectionResource from '@app/core/resources/Connection'
import { Routes } from '../../../routes'
import Breadcrumbs from '@app/components/Breadcrumbs'
import DestinationConnectionTable from './components/DestinationConnectionTable'
import DestinationResource from '@app/core/resources/Destination'
import {
    ItemTabs,
    StepsTypes,
    TableItemTitle,
} from '@app/components/ConnectorBlocks'
import DestinationSettings from './components/DestinationSettings'
import LoadingPage from '@app/components/LoadingPage'
import SourceResource from '@app/core/resources/Source'
import MainPageWithScroll from '@app/components/MainPageWithScroll'
import DestinationDefinitionResource from '@app/core/resources/DestinationDefinition'
import { getIcon } from '@app/utils/imageUtils'
import ImageBlock from '@app/components/ImageBlock'
import SourceDefinitionResource from '@app/core/resources/SourceDefinition'
import HeadTitle from '@app/components/HeadTitle'
import useWorkspace from '@app/hooks/services/useWorkspace'
import { DropDownRow } from '@app/components'

const DestinationItemPage: React.FC = () => {
    const { query, push } = useRouter<{ id: string }>()
    const { workspace } = useWorkspace()
    const [currentStep, setCurrentStep] = useState<string>(StepsTypes.OVERVIEW)
    const onSelectStep = (id: string) => setCurrentStep(id)

    const { sources } = useResource(SourceResource.listShape(), {
        workspaceId: workspace.workspaceId,
    })

    const { sourceDefinitions } = useResource(
        SourceDefinitionResource.listShape(),
        {
            workspaceId: workspace.workspaceId,
        }
    )

    const destination = useResource(DestinationResource.detailShape(), {
        destinationId: query.id,
    })

    const destinationDefinition = useResource(
        DestinationDefinitionResource.detailShape(),
        {
            destinationDefinitionId: destination.destinationDefinitionId,
        }
    )

    const { connections } = useResource(ConnectionResource.listShape(), {
        workspaceId: workspace.workspaceId,
    })

    const onClickBack = () => push(Routes.Destination)

    const breadcrumbsData = [
        {
            name: <FormattedMessage id="admin.destinations" />,
            onClick: onClickBack,
        },
        { name: destination.name },
    ]

    const connectionsWithDestination = connections.filter(
        (connectionItem) =>
            connectionItem.destinationId === destination.destinationId
    )

    const sourcesDropDownData = useMemo(
        () =>
            sources.map((item) => {
                const sourceDef = sourceDefinitions.find(
                    (sd) => sd.sourceDefinitionId === item.sourceDefinitionId
                )
                return {
                    label: item.name,
                    value: item.sourceId,
                    img: <ImageBlock img={sourceDef?.icon} />,
                }
            }),
        [sources, sourceDefinitions]
    )

    const onSelect = (data: DropDownRow.IDataItem) => {
        if (data.value === 'create-new-item') {
            push({
                pathname: `${Routes.Destination}${Routes.ConnectionNew}`,
                state: { destinationId: destination.destinationId },
            })
        } else {
            push({
                pathname: `${Routes.Destination}${Routes.ConnectionNew}`,
                state: {
                    sourceId: data.value,
                    destinationId: destination.destinationId,
                },
            })
        }
    }

    const renderContent = () => {
        if (currentStep === StepsTypes.SETTINGS) {
            return (
                <DestinationSettings
                    currentDestination={destination}
                    connectionsWithDestination={connectionsWithDestination}
                />
            )
        }

        return (
            <>
                <TableItemTitle
                    type="source"
                    dropDownData={sourcesDropDownData}
                    onSelect={onSelect}
                    entityName={destination.name}
                    entity={destination.destinationName}
                    entityIcon={
                        destinationDefinition.icon
                            ? getIcon(destinationDefinition.icon)
                            : null
                    }
                />
                {connectionsWithDestination.length ? (
                    <DestinationConnectionTable
                        connections={connectionsWithDestination}
                    />
                ) : (
                    <Placeholder resource={ResourceTypes.Sources} />
                )}
            </>
        )
    }

    return (
        <MainPageWithScroll
            headTitle={
                <HeadTitle
                    titles={[
                        { id: 'admin.destinations' },
                        { title: destination.name },
                    ]}
                />
            }
            pageTitle={
                <PageTitle
                    title={<Breadcrumbs data={breadcrumbsData} />}
                    withLine
                    middleComponent={
                        <ItemTabs
                            currentStep={currentStep}
                            setCurrentStep={onSelectStep}
                        />
                    }
                />
            }
        >
            <Suspense fallback={<LoadingPage />}>{renderContent()}</Suspense>
        </MainPageWithScroll>
    )
}

export default DestinationItemPage
