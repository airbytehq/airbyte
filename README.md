# Airbyte-Enterprise

This is the closed-source equivalent to [airbytehq/airbyte](https://github.com/airbytehq/airbyte).
Tools like gradle, airbyte-ci, etc. are expected to behave in exactly the same way.

## Git Submodule Setup

This repo has `airbytehq/airbyte` as a submodule, located in `airbyte-submodule`,
and then a lot of symlinks pointing inside of there to make gradle and airbyte-ci magically work
just the same.

After cloning this repo, initialize the submodule with:
```shell
cd airbyte-enterprise
git submodule init
git submodule update --remote`
```

Then, simply never touch it.
Git submodules are a regular source of annoyance for developers of all kinds.

Should it happen that the submodule becomes _dirty_ because some file was changed unintentionally:
```shell
cd airbyte-submodule
git reset --hard
git clean -f -d
cd ..
```

Further reading on git submodules:
- https://www.cyberdemon.org/2024/03/20/submodules.html
- https://www.atlassian.com/git/tutorials/git-submodule
- https://git-scm.com/book/en/v2/Git-Tools-Submodules
- https://git-scm.com/docs/git-submodule
