#define GIT_STASH_APPLY_OPTIONS_VERSION 1
#define GIT_STASH_SAVE_OPTIONS_VERSION ...

typedef int (*git_stash_cb)(
	size_t index,
	const char* message,
	const git_oid *stash_id,
	void *payload);

typedef enum {
	GIT_STASH_APPLY_PROGRESS_NONE = 0,
	GIT_STASH_APPLY_PROGRESS_LOADING_STASH,
	GIT_STASH_APPLY_PROGRESS_ANALYZE_INDEX,
	GIT_STASH_APPLY_PROGRESS_ANALYZE_MODIFIED,
	GIT_STASH_APPLY_PROGRESS_ANALYZE_UNTRACKED,
	GIT_STASH_APPLY_PROGRESS_CHECKOUT_UNTRACKED,
	GIT_STASH_APPLY_PROGRESS_CHECKOUT_MODIFIED,
	GIT_STASH_APPLY_PROGRESS_DONE,
} git_stash_apply_progress_t;

typedef int (*git_stash_apply_progress_cb)(
	git_stash_apply_progress_t progress,
	void *payload);

typedef enum {
	GIT_STASH_DEFAULT = 0,
	GIT_STASH_KEEP_INDEX = 1,
	GIT_STASH_INCLUDE_UNTRACKED = 2,
	GIT_STASH_INCLUDE_IGNORED = 4,
	GIT_STASH_KEEP_ALL = 8,
} git_stash_flags;

typedef enum {
	GIT_STASH_APPLY_DEFAULT = 0,
	GIT_STASH_APPLY_REINSTATE_INDEX = 1,
} git_stash_apply_flags;

typedef struct git_stash_apply_options {
	unsigned int version;
	git_stash_apply_flags flags;
	git_checkout_options checkout_options;
	git_stash_apply_progress_cb progress_cb;
	void *progress_payload;
} git_stash_apply_options;

int git_stash_save(
	git_oid *out,
	git_repository *repo,
	const git_signature *stasher,
	const char *message,
	uint32_t flags);

int git_stash_apply_options_init(
	git_stash_apply_options *opts, unsigned int version);

int git_stash_apply(
	git_repository *repo,
	size_t index,
	const git_stash_apply_options *options);

typedef struct git_stash_save_options {
	unsigned int version;
	uint32_t flags;
	const git_signature *stasher;
	const char *message;
	git_strarray paths;
} git_stash_save_options;

int git_stash_save_options_init(
	git_stash_save_options *opts,
	unsigned int version);

int git_stash_save_with_opts(
	git_oid *out,
	git_repository *repo,
	const git_stash_save_options *opts);

int git_stash_foreach(
	git_repository *repo,
	git_stash_cb callback,
	void *payload);

int git_stash_drop(
	git_repository *repo,
	size_t index);

int git_stash_pop(
	git_repository *repo,
	size_t index,
	const git_stash_apply_options *options);
