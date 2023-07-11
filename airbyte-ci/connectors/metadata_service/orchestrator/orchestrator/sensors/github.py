from datetime import datetime
from dagster import sensor, RunRequest, SkipReason, SensorDefinition, SensorEvaluationContext, build_resources, DefaultSensorStatus

# e.g. 2023-06-02T17:42:36Z
EXPECTED_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def github_connector_nightly_workflow_run_sensor(job, resources_def) -> SensorDefinition:
    """
    This sensor is responsible for polling the github connector nightly workflow for new runs.
    """

    @sensor(
        name=f"{job.name}_on_github_connector_nightly_workflow_success",
        job=job,
        minimum_interval_seconds=(1 * 60 * 60),
        default_status=DefaultSensorStatus.STOPPED,
    )
    def github_connector_nightly_workflow_run_sensor_definition(context: SensorEvaluationContext):
        context.log.info("Starting github_connector_nightly_workflow_run_sensor")

        with build_resources(resources_def) as resources:
            context.log.info("Got resources for github_connector_nightly_workflow_run_sensor")

            context.log.info(f"Old cursor: {context.cursor}")

            # convert the string cursor to a datetime object
            cursor_as_datetime = datetime.strptime(context.cursor, EXPECTED_DATETIME_FORMAT) if context.cursor else None

            latest_successful_workflow_runs = resources.github_connector_nightly_workflow_successes

            # get all latest updated at value from the latest_successful_workflow_runs
            last_successful_run_date = max(
                [datetime.strptime(run["updated_at"], EXPECTED_DATETIME_FORMAT) for run in latest_successful_workflow_runs]
            )

            is_new_run = not cursor_as_datetime or cursor_as_datetime < last_successful_run_date

            if not is_new_run:
                return SkipReason("No new successful workflow runs in github")

            new_cursor = last_successful_run_date.strftime(EXPECTED_DATETIME_FORMAT)

            context.update_cursor(new_cursor)
            run_key = f"new_successful_workflow_run:{new_cursor}"
            return RunRequest(run_key=run_key)

    return github_connector_nightly_workflow_run_sensor_definition
