import React, { Suspense } from 'react'
import { FormattedMessage } from 'react-intl'
import { useResource } from 'rest-hooks'

import PageTitle from '@app/components/PageTitle'
import HeadTitle from '@app/components/HeadTitle'
import useRouter from '@app/hooks/useRouter'
import StepsMenu from '@app/components/StepsMenu'
import StatusView from './components/StatusView'
import SettingsView from './components/SettingsView'
import ConnectionResource from '@app/core/resources/Connection'
import LoadingPage from '@app/components/LoadingPage'
import MainPageWithScroll from '@app/components/MainPageWithScroll'
import FrequencyConfig from '@app/config/FrequencyConfig.json'
import Link from '@app/components/Link'
import { Routes } from '../../../routes'
import DestinationDefinitionResource from '@app/core/resources/DestinationDefinition'
import SourceDefinitionResource from '@app/core/resources/SourceDefinition'
import { equal } from '@app/utils/objects'
import { useAnalytics } from '@app/hooks/useAnalytics'

type ConnectionItemPageProps = {
    currentStep: 'status' | 'settings'
}

const ConnectionItemPage: React.FC<ConnectionItemPageProps> = ({
    currentStep,
}) => {
    const { query, push } = useRouter<{ id: string }>()
    const analyticsService = useAnalytics()
    const connection = useResource(ConnectionResource.detailShape(), {
        connectionId: query.id,
    })

    const frequency = FrequencyConfig.find((item) =>
        equal(item.config, connection.schedule)
    )

    const { source, destination } = connection

    const sourceDefinition = useResource(
        SourceDefinitionResource.detailShape(),
        source
            ? {
                  sourceDefinitionId: source.sourceDefinitionId,
              }
            : null
    )

    const destinationDefinition = useResource(
        DestinationDefinitionResource.detailShape(),
        destination
            ? {
                  destinationDefinitionId: destination.destinationDefinitionId,
              }
            : null
    )

    const steps = [
        {
            id: 'status',
            name: <FormattedMessage id={'sources.status'} />,
        },
        {
            id: 'settings',
            name: <FormattedMessage id={'sources.settings'} />,
        },
    ]

    const onSelectStep = (id: string) => {
        if (id === 'settings') {
            push(
                `${Routes.Connections}/${connection.connectionId}${Routes.Settings}`
            )
        } else {
            push(`${Routes.Connections}/${connection.connectionId}`)
        }
    }

    const onAfterSaveSchema = () => {
        analyticsService.track('Source - Action', {
            action: 'Edit schema',
            connector_source: source.sourceName,
            connector_source_id: source.sourceDefinitionId,
            connector_destination: destination.destinationName,
            connector_destination_definition_id:
                destination.destinationDefinitionId,
            frequency: frequency?.text,
        })
    }

    const renderStep = () => {
        if (currentStep === 'status') {
            return (
                <StatusView
                    connection={connection}
                    frequencyText={frequency?.text}
                    sourceDefinition={sourceDefinition}
                    destinationDefinition={destinationDefinition}
                />
            )
        }

        return (
            <SettingsView
                onAfterSaveSchema={onAfterSaveSchema}
                connectionId={connection.connectionId}
                frequencyText={frequency?.text}
                sourceDefinition={sourceDefinition}
                destinationDefinition={destinationDefinition}
            />
        )
    }

    const linkToSource = () => (
        <Link $clear to={`${Routes.Source}/${source.sourceId}`}>
            {source.name}
        </Link>
    )

    const linkToDestination = () => (
        <Link $clear to={`${Routes.Destination}/${destination.destinationId}`}>
            {destination.name}
        </Link>
    )

    return (
        <MainPageWithScroll
            headTitle={
                <HeadTitle
                    titles={[
                        { id: 'sidebar.connections' },
                        {
                            id: 'connection.fromTo',
                            values: {
                                source: source.name,
                                destination: destination.name,
                            },
                        },
                    ]}
                />
            }
            pageTitle={
                <PageTitle
                    withLine
                    title={
                        <FormattedMessage
                            id="connection.fromTo"
                            values={{
                                source: linkToSource(),
                                destination: linkToDestination(),
                            }}
                        />
                    }
                    middleComponent={
                        <StepsMenu
                            lightMode
                            data={steps}
                            onSelect={onSelectStep}
                            activeStep={currentStep}
                        />
                    }
                />
            }
        >
            <Suspense fallback={<LoadingPage />}>{renderStep()}</Suspense>
        </MainPageWithScroll>
    )
}

export default ConnectionItemPage
