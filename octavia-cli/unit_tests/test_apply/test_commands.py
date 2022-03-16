#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from click.testing import CliRunner
from octavia_cli.apply import commands


@pytest.fixture
def patch_click(mocker):
    mocker.patch.object(commands, "click")


@pytest.fixture
def context_object(mock_api_client):
    return {"PROJECT_IS_INITIALIZED": True, "API_CLIENT": mock_api_client, "WORKSPACE_ID": "workspace_id"}


def test_apply_not_initialized():
    runner = CliRunner()
    result = runner.invoke(commands.apply, obj={"PROJECT_IS_INITIALIZED": False})
    assert result.exit_code == 1


def test_apply_without_custom_configuration_file(mocker, context_object):
    runner = CliRunner()
    local_files = ["foo", "bar"]
    mocker.patch.object(commands, "find_local_configuration_files", mocker.Mock(return_value=local_files))
    mock_resources_to_apply = [mocker.Mock(), mocker.Mock()]
    mocker.patch.object(commands, "get_resources_to_apply", mocker.Mock(return_value=mock_resources_to_apply))
    mocker.patch.object(commands, "apply_single_resource")
    result = runner.invoke(commands.apply, obj=context_object)
    assert result.exit_code == 0
    commands.find_local_configuration_files.assert_called_once()
    commands.get_resources_to_apply.assert_called_once_with(local_files, context_object["API_CLIENT"], context_object["WORKSPACE_ID"])
    commands.apply_single_resource([mocker.call(r, False) for r in commands.get_resources_to_apply.return_value])


def test_apply_with_custom_configuration_file(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "find_local_configuration_files")
    mocker.patch.object(commands, "get_resources_to_apply")
    mocker.patch.object(commands, "apply_single_resource")
    result = runner.invoke(commands.apply, ["--file", "foo", "--file", "bar"], obj=context_object)
    assert result.exit_code == 0
    commands.find_local_configuration_files.assert_not_called()
    commands.get_resources_to_apply.assert_called_with(("foo", "bar"), context_object["API_CLIENT"], context_object["WORKSPACE_ID"])


def test_apply_with_custom_configuration_file_force(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "find_local_configuration_files")
    mocker.patch.object(commands, "get_resources_to_apply", mocker.Mock(return_value=[mocker.Mock()]))
    mocker.patch.object(commands, "apply_single_resource")
    result = runner.invoke(commands.apply, ["--file", "foo", "--file", "bar", "--force"], obj=context_object)
    assert result.exit_code == 0
    commands.apply_single_resource.assert_called_with(commands.get_resources_to_apply.return_value[0], True)


def test_get_resource_to_apply(mocker, mock_api_client):
    local_files_priorities = [("foo", 2), ("bar", 1)]
    mock_resource_factory = mocker.Mock()
    mock_resource_factory.side_effect = [mocker.Mock(APPLY_PRIORITY=priority) for _, priority in local_files_priorities]
    mocker.patch.object(commands, "resource_factory", mock_resource_factory)

    resources_to_apply = commands.get_resources_to_apply([f[0] for f in local_files_priorities], mock_api_client, "workspace_id")
    assert resources_to_apply == sorted(resources_to_apply, key=lambda r: r.APPLY_PRIORITY)
    assert commands.resource_factory.call_count == len(local_files_priorities)
    commands.resource_factory.assert_has_calls([mocker.call(mock_api_client, "workspace_id", path) for path, _ in local_files_priorities])


@pytest.mark.parametrize("resource_was_created", [True, False])
def test_apply_single_resource(patch_click, mocker, resource_was_created):
    mocker.patch.object(commands, "update_resource", mocker.Mock(return_value=["updated"]))
    mocker.patch.object(commands, "create_resource", mocker.Mock(return_value=["created"]))
    resource = mocker.Mock(was_created=resource_was_created, resource_name="my_resource_name")
    force = mocker.Mock()
    commands.apply_single_resource(resource, force)
    if resource_was_created:
        commands.update_resource.assert_called_once_with(resource, force)
        commands.create_resource.assert_not_called()
        expected_message = "🐙 - my_resource_name exists on your Airbyte instance, let's check if we need to update it!"
        expected_message_color = "yellow"
        expected_echo_calls = [mocker.call(commands.click.style.return_value), mocker.call("\n".join(["updated"]))]
    else:
        commands.update_resource.assert_not_called()
        commands.create_resource.assert_called_once_with(resource)
        expected_message = "🐙 - my_resource_name does not exists on your Airbyte instance, let's create it!"
        expected_message_color = "green"
        expected_echo_calls = [mocker.call(commands.click.style.return_value), mocker.call("\n".join(["created"]))]
    commands.click.style.assert_called_with(expected_message, fg=expected_message_color)
    commands.click.echo.assert_has_calls(expected_echo_calls)


@pytest.mark.parametrize(
    "diff,local_file_changed,force,expected_should_update,expected_update_reason",
    [
        (True, True, True, True, "🚨 - Running update because force mode is on."),  # check if force has the top priority
        (True, False, True, True, "🚨 - Running update because force mode is on."),  # check if force has the top priority
        (True, False, False, True, "🚨 - Running update because force mode is on."),  # check if force has the top priority
        (True, True, False, True, "🚨 - Running update because force mode is on."),  # check if force has the top priority
        (
            False,
            True,
            True,
            True,
            "✍️ - Running update because a diff was detected between local and remote resource.",
        ),  # check if diff has priority of file changed
        (
            False,
            True,
            False,
            True,
            "✍️ - Running update because a diff was detected between local and remote resource.",
        ),  # check if diff has priority of file changed
        (
            False,
            False,
            True,
            True,
            "✍️ - Running update because a local file change was detected and a secret field might have been edited.",
        ),  # check if local_file_changed runs even if no diff found
        (
            False,
            False,
            False,
            False,
            "😴 - Did not update because no change detected.",
        ),  # check if local_file_changed runs even if no diff found
    ],
)
def test_should_update_resource(patch_click, mocker, diff, local_file_changed, force, expected_should_update, expected_update_reason):
    should_update, update_reason = commands.should_update_resource(diff, local_file_changed, force)
    assert should_update == expected_should_update
    assert update_reason == commands.click.style.return_value
    commands.click.style.assert_called_with(expected_update_reason, fg="green")


@pytest.mark.parametrize(
    "diff,expected_number_calls_to_display_diff_line",
    [("", 0), ("First diff line", 1), ("First diff line\nSecond diff line", 2), ("First diff line\nSecond diff line\nThird diff line", 3)],
)
def test_prompt_for_diff_validation(patch_click, mocker, diff, expected_number_calls_to_display_diff_line):
    mocker.patch.object(commands, "display_diff_line")
    output = commands.prompt_for_diff_validation("my_resource", diff)
    assert commands.display_diff_line.call_count == expected_number_calls_to_display_diff_line
    if diff and expected_number_calls_to_display_diff_line > 0:
        commands.display_diff_line.assert_has_calls([mocker.call(line) for line in diff.split("\n")])
        commands.click.style.assert_has_calls(
            [
                mocker.call(
                    "👀 - Here's the computed diff (🚨 remind that diff on secret fields are not displayed):", fg="magenta", bold=True
                ),
                mocker.call("❓ - Do you want to update my_resource?", bold=True),
            ]
        )
        commands.click.echo.assert_called_with(commands.click.style.return_value)
        assert output == commands.click.confirm.return_value
    else:
        assert output is False


def test_create_resource(patch_click, mocker):
    mock_created_resource = mocker.Mock()
    mock_state = mocker.Mock()
    mock_resource = mocker.Mock(create=mocker.Mock(return_value=(mock_created_resource, mock_state)))
    output_messages = commands.create_resource(mock_resource)
    mock_resource.create.assert_called_once()
    assert output_messages == [commands.click.style.return_value, commands.click.style.return_value]
    commands.click.style.assert_has_calls(
        [
            mocker.call(f"🎉 - Successfully created {mock_created_resource.name} on your Airbyte instance!", fg="green", bold=True),
            mocker.call(f"💾 - New state for {mock_created_resource.name} saved at {mock_state.path}", fg="yellow"),
        ]
    )


@pytest.mark.parametrize(
    "force,diff,should_update_resource,expect_prompt,user_validate_diff,expect_update,expected_number_of_messages",
    [
        (True, True, True, False, False, True, 3),  # Force is on, we have a diff, prompt should not be displayed: we expect update.
        (
            True,
            False,
            True,
            False,
            False,
            True,
            3,
        ),  # Force is on, no diff, should_update_resource == true, prompt should not be displayed, we expect update.
        (
            True,
            False,
            False,
            False,
            False,
            False,
            1,
        ),  # Force is on, no diff, should_update_resource == false, prompt should not be displayed, we don't expect update. This scenario should not exists in current implementation as force always trigger update.
        (
            False,
            True,
            True,
            True,
            True,
            True,
            3,
        ),  # Force is off, we have diff, prompt should be displayed, user validate diff: we expected update.
        (
            False,
            False,
            True,
            False,
            False,
            True,
            3,
        ),  # Force is off, no diff, should_update_resource == true (in case of file change), prompt should not be displayed, we expect update.
        (
            False,
            True,
            True,
            True,
            False,
            False,
            1,
        ),  # Force is off, we have a diff but the user does not validate it: we don't expect update.
        (
            False,
            False,
            False,
            False,
            False,
            False,
            1,
        ),  # Force is off, we have a no diff, should_update_resource == false: we don't expect update.
    ],
)
def test_update_resource(
    patch_click, mocker, force, diff, should_update_resource, user_validate_diff, expect_prompt, expect_update, expected_number_of_messages
):
    mock_updated_resource = mocker.Mock()
    mock_state = mocker.Mock()
    mock_resource = mocker.Mock(
        get_diff_with_remote_resource=mocker.Mock(return_value=diff),
        resource_name="my_resource",
        update=mocker.Mock(return_value=(mock_updated_resource, mock_state)),
    )
    update_reason = "foo"
    mocker.patch.object(commands, "should_update_resource", mocker.Mock(return_value=(should_update_resource, update_reason)))
    mocker.patch.object(commands, "prompt_for_diff_validation", mocker.Mock(return_value=user_validate_diff))

    output_messages = commands.update_resource(mock_resource, force)
    if expect_prompt:
        commands.prompt_for_diff_validation.assert_called_once_with("my_resource", diff)
    else:
        commands.prompt_for_diff_validation.assert_not_called()
    if expect_update:
        mock_resource.update.assert_called_once()
    else:
        mock_resource.update.assert_not_called()
    assert output_messages[0] == commands.should_update_resource.return_value[1] == update_reason
    assert len(output_messages) == expected_number_of_messages
    if expected_number_of_messages == 3:
        assert output_messages == [
            commands.should_update_resource.return_value[1],
            commands.click.style.return_value,
            commands.click.style.return_value,
        ]
        commands.click.style.assert_has_calls(
            [
                mocker.call(f"🎉 - Successfully updated {mock_updated_resource.name} on your Airbyte instance!", fg="green", bold=True),
                mocker.call(f"💾 - New state for {mock_updated_resource.name} stored at {mock_state.path}.", fg="yellow"),
            ]
        )


def test_find_local_configuration_files(mocker):
    project_directories = ["sources", "connections", "destinations"]
    mocker.patch.object(commands, "REQUIRED_PROJECT_DIRECTORIES", project_directories)
    mocker.patch.object(commands, "glob", mocker.Mock(return_value=["foo.yaml"]))
    configuration_files = commands.find_local_configuration_files()
    assert isinstance(configuration_files, list)
    commands.glob.assert_has_calls([mocker.call(f"./{directory}/**/configuration.yaml") for directory in project_directories])
    assert configuration_files == ["foo.yaml" for _ in range(len(project_directories))]


def test_find_local_configuration_files_no_file_found(patch_click, mocker):
    project_directories = ["sources", "connections", "destinations"]
    mocker.patch.object(commands, "REQUIRED_PROJECT_DIRECTORIES", project_directories)
    mocker.patch.object(commands, "glob", mocker.Mock(return_value=[]))
    configuration_files = commands.find_local_configuration_files()
    assert not configuration_files
    commands.click.style.assert_called_once_with("😒 - No YAML file found to run apply.", fg="red")
