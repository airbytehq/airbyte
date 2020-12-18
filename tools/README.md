# Tools

## Releasing a new version
```
git branch -b your-release-branch
./tools/bin/release_version.sh patch # or minor or major
git push --set-upstream origin your-release-branch
# create PR from branch
# merge PR
git checkout master
./tools/bin/tag_version.sh
```
