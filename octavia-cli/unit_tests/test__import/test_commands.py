#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from click.testing import CliRunner
from octavia_cli._import import commands


@pytest.fixture
def patch_click(mocker):
    mocker.patch.object(commands, "click")


@pytest.fixture
def context_object(mock_api_client, mock_telemetry_client):
    return {
        "PROJECT_IS_INITIALIZED": True,
        "API_CLIENT": mock_api_client,
        "WORKSPACE_ID": "workspace_id",
        "TELEMETRY_CLIENT": mock_telemetry_client,
    }


def test_build_help_message():
    assert commands.build_help_message("source") == "Import an existing source to manage it with octavia-cli."


@pytest.mark.parametrize("ResourceClass", [commands.UnmanagedSource, commands.UnmanagedDestination])
def test_import_source_or_destination(mocker, context_object, ResourceClass):
    resource_type = ResourceClass.__name__.lower()
    mocker.patch.object(commands.click, "style")
    mocker.patch.object(commands.click, "echo")
    mocker.patch.object(commands, "get_json_representation")
    mocker.patch.object(
        commands.json,
        "loads",
        mocker.Mock(
            return_value={
                "name": "foo",
                "connection_configuration": "bar",
                f"{resource_type}_definition_id": f"{resource_type}_definition_id",
                f"{resource_type}_id": f"my_{resource_type}_id",
            }
        ),
    )
    mocker.patch.object(commands.definitions, "factory")
    mocker.patch.object(commands.renderers, "ConnectorSpecificationRenderer")
    expected_managed_resource, expected_state = (mocker.Mock(), mocker.Mock())
    mocker.patch.object(
        commands.resources,
        "factory",
        mocker.Mock(return_value=mocker.Mock(manage=mocker.Mock(return_value=(expected_managed_resource, expected_state)))),
    )
    commands.import_source_or_destination(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], ResourceClass, "resource_to_get")
    commands.get_json_representation.assert_called_with(
        context_object["API_CLIENT"], context_object["WORKSPACE_ID"], ResourceClass, "resource_to_get"
    )
    commands.json.loads.assert_called_with(commands.get_json_representation.return_value)
    remote_configuration = commands.json.loads.return_value
    commands.definitions.factory.assert_called_with(
        resource_type, context_object["API_CLIENT"], context_object["WORKSPACE_ID"], f"{resource_type}_definition_id"
    )
    commands.renderers.ConnectorSpecificationRenderer.assert_called_with("foo", commands.definitions.factory.return_value)
    renderer = commands.renderers.ConnectorSpecificationRenderer.return_value
    renderer.import_configuration.assert_called_with(project_path=".", configuration=remote_configuration["connection_configuration"])
    commands.resources.factory.assert_called_with(
        context_object["API_CLIENT"], context_object["WORKSPACE_ID"], renderer.import_configuration.return_value
    )
    commands.resources.factory.return_value.manage.assert_called_with(remote_configuration[f"{resource_type}_id"])
    commands.click.style.assert_has_calls(
        [
            mocker.call(
                f"✅ - Imported {resource_type} {expected_managed_resource.name} in {renderer.import_configuration.return_value}. State stored in {expected_state.path}",
                fg="green",
            ),
            mocker.call(f"⚠️  - Please update any secrets stored in {renderer.import_configuration.return_value}", fg="yellow"),
        ]
    )
    assert commands.click.echo.call_count == 2


@pytest.mark.parametrize(
    "source_exists, source_was_created, destination_exists, destination_was_created",
    [
        (True, True, True, True),
        (False, False, False, False),
        (True, False, True, False),
        (True, True, False, False),
        (True, True, True, False),
    ],
)
def test_import_connection(mocker, context_object, source_exists, source_was_created, destination_exists, destination_was_created):
    mocker.patch.object(commands.click, "style")
    mocker.patch.object(commands.click, "echo")
    mocker.patch.object(commands, "get_json_representation")
    mocker.patch.object(
        commands.json,
        "loads",
        mocker.Mock(
            return_value={
                "source": {"name": "my_source"},
                "destination": {"name": "my_destination"},
                "name": "my_connection",
                "connection_id": "my_connection_id",
            }
        ),
    )
    remote_configuration = commands.json.loads.return_value
    mocker.patch.object(commands.definitions, "factory")
    mock_source_configuration_path = mocker.Mock(is_file=mocker.Mock(return_value=source_exists))
    mock_destination_configuration_path = mocker.Mock(is_file=mocker.Mock(return_value=destination_exists))

    mocker.patch.object(
        commands.renderers.ConnectorSpecificationRenderer,
        "get_output_path",
        mocker.Mock(side_effect=[mock_source_configuration_path, mock_destination_configuration_path]),
    )
    mocker.patch.object(commands.renderers, "ConnectionRenderer")
    mock_managed_source = mocker.Mock(was_created=source_was_created)
    mock_managed_destination = mocker.Mock(was_created=destination_was_created)
    mock_remote_connection, mock_connection_state = mocker.Mock(), mocker.Mock()
    mock_managed_connection = mocker.Mock(manage=mocker.Mock(return_value=(mock_remote_connection, mock_connection_state)))

    mocker.patch.object(
        commands.resources, "factory", mocker.Mock(side_effect=[mock_managed_source, mock_managed_destination, mock_managed_connection])
    )
    if all([source_exists, destination_exists, source_was_created, destination_was_created]):

        commands.import_connection(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], "resource_to_get")
        commands.get_json_representation.assert_called_with(
            context_object["API_CLIENT"], context_object["WORKSPACE_ID"], commands.UnmanagedConnection, "resource_to_get"
        )
        commands.renderers.ConnectorSpecificationRenderer.get_output_path.assert_has_calls(
            [
                mocker.call(project_path=".", definition_type="source", resource_name="my_source"),
                mocker.call(project_path=".", definition_type="destination", resource_name="my_destination"),
            ]
        )
        commands.resources.factory.assert_has_calls(
            [
                mocker.call(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], mock_source_configuration_path),
                mocker.call(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], mock_destination_configuration_path),
                mocker.call(
                    context_object["API_CLIENT"],
                    context_object["WORKSPACE_ID"],
                    commands.renderers.ConnectionRenderer.return_value.import_configuration.return_value,
                ),
            ]
        )
        commands.renderers.ConnectionRenderer.assert_called_with(
            remote_configuration["name"], mock_managed_source, mock_managed_destination
        )
        commands.renderers.ConnectionRenderer.return_value.import_configuration.assert_called_with(".", remote_configuration)
        new_configuration_path = commands.renderers.ConnectionRenderer.return_value.import_configuration.return_value
        commands.click.style.assert_called_with(
            f"✅ - Imported connection {mock_remote_connection.name} in {new_configuration_path}. State stored in {mock_connection_state.path}",
            fg="green",
        )
        commands.click.echo.assert_called_with(commands.click.style.return_value)
    if not source_exists or not destination_exists:
        with pytest.raises(
            commands.MissingResourceDependencyError,
            match="is not managed by octavia-cli, please import and apply it before importing your connection.",
        ):
            commands.import_connection(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], "resource_to_get")
    if source_exists and destination_exists and (not source_was_created or not destination_was_created):
        with pytest.raises(commands.resources.NonExistingResourceError, match="Please run octavia apply before creating this connection."):
            commands.import_connection(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], "resource_to_get")


@pytest.mark.parametrize("command", [commands.source, commands.destination, commands.connection, commands.all])
def test_import_not_initialized(command):
    runner = CliRunner()
    result = runner.invoke(command, obj={"PROJECT_IS_INITIALIZED": False})
    assert result.exit_code == 1


@pytest.mark.parametrize(
    "command, ResourceClass, import_function",
    [
        (commands.source, commands.UnmanagedSource, "import_source_or_destination"),
        (commands.destination, commands.UnmanagedDestination, "import_source_or_destination"),
        (commands.connection, None, "import_connection"),
    ],
)
def test_import_commands(mocker, context_object, ResourceClass, command, import_function):
    runner = CliRunner()
    mock_import_function = mocker.Mock()
    mocker.patch.object(commands, import_function, mock_import_function)
    result = runner.invoke(command, ["resource_to_import"], obj=context_object)
    if import_function == "import_source_or_destination":
        mock_import_function.assert_called_with(
            context_object["API_CLIENT"], context_object["WORKSPACE_ID"], ResourceClass, "resource_to_import"
        )
    else:
        mock_import_function.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], "resource_to_import")
    assert result.exit_code == 0


def test_import_all(mocker, context_object):
    runner = CliRunner()
    mock_manager = mocker.Mock()
    mocker.patch.object(commands, "import_source_or_destination", mock_manager.import_source_or_destination)
    mocker.patch.object(commands, "import_connection", mock_manager.import_connection)
    mocker.patch.object(
        commands, "UnmanagedSources", return_value=mocker.Mock(get_listing=mocker.Mock(return_value=[("_", "_", "source_resource_id")]))
    )
    mocker.patch.object(
        commands,
        "UnmanagedDestinations",
        return_value=mocker.Mock(get_listing=mocker.Mock(return_value=[("_", "_", "destination_resource_id")])),
    )
    mocker.patch.object(
        commands,
        "UnmanagedConnections",
        return_value=mocker.Mock(get_listing=mocker.Mock(return_value=[("_", "connection_resource_id", "_", "_", "_")])),
    )
    result = runner.invoke(commands.all, obj=context_object)

    commands.UnmanagedSources.return_value.get_listing.assert_called_once()
    commands.UnmanagedDestinations.return_value.get_listing.assert_called_once()
    commands.UnmanagedConnections.return_value.get_listing.assert_called_once()
    assert result.exit_code == 0
    assert mock_manager.mock_calls[0] == mocker.call.import_source_or_destination(
        context_object["API_CLIENT"], "workspace_id", commands.UnmanagedSource, "source_resource_id"
    )
    assert mock_manager.mock_calls[1] == mocker.call.import_source_or_destination(
        context_object["API_CLIENT"], "workspace_id", commands.UnmanagedDestination, "destination_resource_id"
    )
    assert mock_manager.mock_calls[2] == mocker.call.import_connection(
        context_object["API_CLIENT"], "workspace_id", "connection_resource_id"
    )
