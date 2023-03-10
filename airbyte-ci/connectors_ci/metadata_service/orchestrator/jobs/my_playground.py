import os
from dagster import op, job, sensor, RunRequest, Definitions, DefaultSensorStatus

MY_DIRECTORY = "/tmp/dagster_test"

@op(config_schema={"filename": str})
def process_file(context):
    filename = context.op_config["filename"]
    context.log.info(filename)


@job
def log_file_job():
    process_file()


@sensor(name="dir_sensor", job=log_file_job, default_status=DefaultSensorStatus.STOPPED)
def my_directory_sensor():
    for filename in os.listdir(MY_DIRECTORY):
        filepath = os.path.join(MY_DIRECTORY, filename)
        if os.path.isfile(filepath):
            yield RunRequest(
                run_key=filename,
                run_config={
                    "ops": {"process_file": {"config": {"filename": filename}}}
                },
            )

defn = Definitions(
    # assets=all_assets,
    # resources=resources_by_deployment_name[deployment_name],
    # schedules=[core_assets_schedule],
    sensors=[my_directory_sensor],
)
