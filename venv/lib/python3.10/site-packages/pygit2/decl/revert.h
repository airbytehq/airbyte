int git_revert_commit(
	git_index **out,
	git_repository *repo,
	git_commit *revert_commit,
	git_commit *our_commit,
	unsigned int mainline,
	const git_merge_options *merge_options);
