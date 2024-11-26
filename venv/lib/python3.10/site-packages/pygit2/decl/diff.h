typedef struct git_diff git_diff;

typedef enum {
	GIT_DELTA_UNMODIFIED = 0,
	GIT_DELTA_ADDED = 1,
	GIT_DELTA_DELETED = 2,
	GIT_DELTA_MODIFIED = 3,
	GIT_DELTA_RENAMED = 4,
	GIT_DELTA_COPIED = 5,
	GIT_DELTA_IGNORED = 6,
	GIT_DELTA_UNTRACKED = 7,
	GIT_DELTA_TYPECHANGE = 8,
	GIT_DELTA_UNREADABLE = 9,
	GIT_DELTA_CONFLICTED = 10,
} git_delta_t;

typedef struct {
	git_oid     id;
	const char *path;
	git_off_t   size;
	uint32_t    flags;
	uint16_t    mode;
	uint16_t    id_abbrev;
} git_diff_file;

typedef struct {
	git_delta_t   status;
	uint32_t      flags;
	uint16_t      similarity;
	uint16_t      nfiles;
	git_diff_file old_file;
	git_diff_file new_file;
} git_diff_delta;

typedef int (*git_diff_notify_cb)(
	const git_diff *diff_so_far,
	const git_diff_delta *delta_to_add,
	const char *matched_pathspec,
	void *payload);

typedef int (*git_diff_progress_cb)(
	const git_diff *diff_so_far,
	const char *old_path,
	const char *new_path,
	void *payload);

typedef struct {
	unsigned int version;
	uint32_t flags;
	git_submodule_ignore_t ignore_submodules;
	git_strarray       pathspec;
	git_diff_notify_cb   notify_cb;
	git_diff_progress_cb progress_cb;
	void                *payload;
	uint32_t    context_lines;
	uint32_t    interhunk_lines;
	git_oid_t   oid_type;
	uint16_t    id_abbrev;
	git_off_t   max_size;
	const char *old_prefix;
	const char *new_prefix;
} git_diff_options;

int git_diff_options_init(
	git_diff_options *opts,
	unsigned int version);

typedef struct {
	int (*file_signature)(
		void **out, const git_diff_file *file,
		const char *fullpath, void *payload);
	int (*buffer_signature)(
		void **out, const git_diff_file *file,
		const char *buf, size_t buflen, void *payload);
	void (*free_signature)(void *sig, void *payload);
	int (*similarity)(int *score, void *siga, void *sigb, void *payload);
	void *payload;
} git_diff_similarity_metric;

int git_diff_tree_to_index(
	git_diff **diff,
	git_repository *repo,
	git_tree *old_tree,
	git_index *index,
	const git_diff_options *opts);

int git_diff_index_to_workdir(
	git_diff **diff,
	git_repository *repo,
	git_index *index,
	const git_diff_options *opts);
