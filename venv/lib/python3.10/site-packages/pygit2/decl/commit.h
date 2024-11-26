int git_commit_amend(
    git_oid *id,
    const git_commit *commit_to_amend,
    const char *update_ref,
    const git_signature *author,
    const git_signature *committer,
    const char *message_encoding,
    const char *message,
    const git_tree *tree);

int git_annotated_commit_lookup(
	git_annotated_commit **out,
	git_repository *repo,
	const git_oid *id);

void git_annotated_commit_free(git_annotated_commit *commit);
