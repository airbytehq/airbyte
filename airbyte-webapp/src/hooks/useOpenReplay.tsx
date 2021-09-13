import { useMemo } from 'react'
import Tracker, { Options } from '@asayerio/tracker'

type MockTracker = {
    use: () => void
    active: () => void
    start: () => void
    stop: () => void
    sessionID: () => void
    userID: () => void
    userAnonymousID: () => void
    metadata: () => void
    event: () => void
    issue: () => void
    handleError: () => void
    handleErrorEvent: () => void
}

let tracker: Tracker | MockTracker = {
    use: () => {},
    active: () => {},
    start: () => {},
    stop: () => {},
    sessionID: () => {},
    userID: () => {},
    userAnonymousID: () => {},
    metadata: () => {},
    event: () => {},
    issue: () => {},
    handleError: () => {},
    handleErrorEvent: () => {},
}

const useTracker = (options: Options): Tracker | MockTracker => {
    return useMemo(() => {
        if (!tracker && process.env.NODE_ENV === 'production') {
            tracker = new Tracker(options)

            tracker.start()
        }

        return tracker
    }, [options])
}

export default useTracker
