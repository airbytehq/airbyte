DELETE
FROM
    jobs
WHERE
    jobs.id IN(
        SELECT
            jobs.id
        FROM
            jobs
        LEFT JOIN(
                SELECT
                    SCOPE,
                    COUNT( jobs.id ) AS jobCount
                FROM
                    jobs
                GROUP BY
                    SCOPE
            ) counts ON
            jobs.scope = counts.scope
        WHERE
            /* job must be at least MINIMUM_AGE_IN_DAYS old or connection has more than EXCESSIVE_NUMBER_OF_JOBS */
            (
                jobs.created_at <(
                    TO_TIMESTAMP(
                        ?,
                        'YYYY-MM-DD'
                    )- INTERVAL '%d' DAY
                )
                OR counts.jobCount >?
            )
            AND jobs.id NOT IN(
                /* cannot be the most recent job with saved state */
                SELECT
                    job_id AS latest_job_id_with_state
                FROM
                    (
                        SELECT
                            jobs.scope,
                            jobs.id AS job_id,
                            jobs.config_type,
                            jobs.created_at,
                            jobs.status,
                            bool_or(
                                attempts."output" -> 'sync' -> 'state' -> 'state' IS NOT NULL
                            ) AS outputStateExists,
                            ROW_NUMBER() OVER(
                                PARTITION BY SCOPE
                            ORDER BY
                                jobs.created_at DESC,
                                jobs.id DESC
                            ) AS stateRecency
                        FROM
                            jobs
                        LEFT JOIN attempts ON
                            jobs.id = attempts.job_id
                        GROUP BY
                            SCOPE,
                            jobs.id
                        HAVING
                            bool_or(
                                attempts."output" -> 'sync' -> 'state' -> 'state' IS NOT NULL
                            )= TRUE
                        ORDER BY
                            SCOPE,
                            jobs.created_at DESC,
                            jobs.id DESC
                    ) jobs_with_state
                WHERE
                    stateRecency = 1
            )
            AND jobs.id NOT IN(
                /* cannot be one of the last MINIMUM_RECENCY jobs for that connection/scope */
                SELECT
                    id
                FROM
                    (
                        SELECT
                            jobs.scope,
                            jobs.id,
                            jobs.created_at,
                            ROW_NUMBER() OVER(
                                PARTITION BY SCOPE
                            ORDER BY
                                jobs.created_at DESC,
                                jobs.id DESC
                            ) AS recency
                        FROM
                            jobs
                        GROUP BY
                            SCOPE,
                            jobs.id
                        ORDER BY
                            SCOPE,
                            jobs.created_at DESC,
                            jobs.id DESC
                    ) jobs_by_recency
                WHERE
                    recency <=?
            )
    )
