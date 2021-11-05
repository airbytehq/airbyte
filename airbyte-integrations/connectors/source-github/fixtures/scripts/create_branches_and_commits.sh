#!/bin/bash

touch ".gitignore"
git add ".gitignore"
git commit -m "Initial commit"
git push origin master

for (( i = 0; i < 5; i++ )); do
    git branch "feature/branch_$i"
done

for (( i = 0; i < 5; i++ )); do
  git checkout "feature/branch_$i"
    mkdir github_sources
    for (( j = 0; j < 5; j++ )); do
        echo "text_for_file_$j_commit" > "github_sources/file_$j.txt"
        git add github_sources
        git commit -m "commit number $j"
        git push origin "feature/branch_$i"
    done
done