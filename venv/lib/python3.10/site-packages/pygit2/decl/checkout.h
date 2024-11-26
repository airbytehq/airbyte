typedef enum {
	GIT_CHECKOUT_NOTIFY_NONE      = 0,
	GIT_CHECKOUT_NOTIFY_CONFLICT  = 1,
	GIT_CHECKOUT_NOTIFY_DIRTY     = 2,
	GIT_CHECKOUT_NOTIFY_UPDATED   = 4,
	GIT_CHECKOUT_NOTIFY_UNTRACKED = 8,
	GIT_CHECKOUT_NOTIFY_IGNORED   = 16,

	GIT_CHECKOUT_NOTIFY_ALL       = 0x0FFFF
} git_checkout_notify_t;

typedef int (*git_checkout_notify_cb)(
	git_checkout_notify_t why,
	const char *path,
	const git_diff_file *baseline,
	const git_diff_file *target,
	const git_diff_file *workdir,
	void *payload);

typedef void (*git_checkout_progress_cb)(
	const char *path,
	size_t completed_steps,
	size_t total_steps,
	void *payload);

typedef struct {
	size_t mkdir_calls;
	size_t stat_calls;
	size_t chmod_calls;
} git_checkout_perfdata;

typedef void (*git_checkout_perfdata_cb)(
	const git_checkout_perfdata *perfdata,
	void *payload);

typedef struct git_checkout_options {
	unsigned int version;

	unsigned int checkout_strategy;

	int disable_filters;
	unsigned int dir_mode;
	unsigned int file_mode;
	int file_open_flags;

	unsigned int notify_flags;
	git_checkout_notify_cb notify_cb;
	void *notify_payload;

	git_checkout_progress_cb progress_cb;
	void *progress_payload;

	git_strarray paths;

	git_tree *baseline;

	git_index *baseline_index;

	const char *target_directory;

	const char *ancestor_label;
	const char *our_label;
	const char *their_label;

	git_checkout_perfdata_cb perfdata_cb;
	void *perfdata_payload;
} git_checkout_options;


int git_checkout_options_init(
	git_checkout_options *opts,
	unsigned int version);

int git_checkout_tree(
	git_repository *repo,
	const git_object *treeish,
	const git_checkout_options *opts);

int git_checkout_head(
	git_repository *repo,
	const git_checkout_options *opts);

int git_checkout_index(
	git_repository *repo,
	git_index *index,
	const git_checkout_options *opts);

