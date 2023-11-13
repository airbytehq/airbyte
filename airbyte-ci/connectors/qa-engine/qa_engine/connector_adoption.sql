WITH official_connector_syncs AS(
    SELECT
        *
    FROM
        airbyte_warehouse.connector_sync
    WHERE
        is_officially_published
        AND(
            job_status = "failed"
            OR job_status = "succeeded"
        )
),
adoption_per_version AS(
    SELECT
        connector_definition_id,
        docker_repository,
        connector_version,
        COUNT( DISTINCT( user_id )) AS number_of_users,
        COUNT( DISTINCT( connection_id )) AS number_of_connections
    FROM
        official_connector_syncs
    GROUP BY
        connector_definition_id,
        docker_repository,
        connector_version
),
job_status_per_version AS(
    SELECT
        connector_definition_id,
        docker_repository,
        connector_version,
        job_status,
        COUNT( 1 ) AS sync_count
    FROM
        official_connector_syncs
    GROUP BY
        connector_definition_id,
        docker_repository,
        connector_version,
        job_status
),
success_failure_by_connector_version AS(
    SELECT
        connector_definition_id,
        docker_repository,
        connector_version,
        ifnull(
            failed,
            0
        ) AS failed_syncs_count,
        ifnull(
            succeeded,
            0
        ) AS succeeded_syncs_count,
        ifnull(
            succeeded,
            0
        )+ ifnull(
            failed,
            0
        ) AS total_syncs_count,
        SAFE_DIVIDE(
            ifnull(
                succeeded,
                0
            ),
            ifnull(
                succeeded,
                0
            )+ ifnull(
                failed,
                0
            )
        ) AS sync_success_rate
    FROM
        job_status_per_version PIVOT(
            MAX( sync_count ) FOR job_status IN(
                'failed',
                'succeeded'
            )
        )
) SELECT
    *
FROM
    adoption_per_version
LEFT JOIN success_failure_by_connector_version
        USING(
        connector_definition_id,
        docker_repository,
        connector_version
    );
