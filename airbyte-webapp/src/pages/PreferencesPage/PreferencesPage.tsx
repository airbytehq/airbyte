import React, { useEffect } from 'react'
import { FormattedMessage } from 'react-intl'
import styled from 'styled-components'

import { PageViewContainer } from '@app/components/CenteredPageComponents'
import { H1 } from '@app/components'
import { PreferencesForm } from '@app/views/Settings/PreferencesForm'
import HeadTitle from '@app/components/HeadTitle'
import { useAnalytics } from '@app/hooks/useAnalytics'
import useWorkspace from '@app/hooks/services/useWorkspace'

const Title = styled(H1)`
    margin-bottom: 47px;
`

const PreferencesPage: React.FC = () => {
    const analyticsService = useAnalytics()
    useEffect(
        () => analyticsService.page('Preferences Page'),
        [analyticsService]
    )

    const { setInitialSetupConfig } = useWorkspace()

    const onSubmit = async (data: {
        email: string
        anonymousDataCollection: boolean
        news: boolean
        securityUpdates: boolean
    }) => {
        await setInitialSetupConfig(data)

        analyticsService.track('Specified Preferences', {
            email: data.email,
            anonymized: data.anonymousDataCollection,
            subscribed_newsletter: data.news,
            subscribed_security: data.securityUpdates,
        })
    }

    return (
        <PageViewContainer>
            <HeadTitle titles={[{ id: 'preferences.headTitle' }]} />
            <Title center>
                <FormattedMessage id={'preferences.title'} />
            </Title>
            <PreferencesForm onSubmit={onSubmit} />
        </PageViewContainer>
    )
}

export default PreferencesPage
