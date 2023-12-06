import asyncclick as click

PRE_CONFIRM_KEY = "yes"

def pre_confirm_flag(f):
    """Decorator to add a --yes flag to a command."""
    return click.option("-y", "--yes", PRE_CONFIRM_KEY, is_flag=True, default=False, help="Skip prompts and use default values")(f)

def confirm(*args, **kwargs) -> bool:
    """Confirm a prompt with the user, with support for a --yes flag."""
    ctx = click.get_current_context()
    if ctx.obj.get(PRE_CONFIRM_KEY, False):
        return True

    return click.confirm(*args, **kwargs)
