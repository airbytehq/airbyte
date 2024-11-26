#define GIT_CLONE_OPTIONS_VERSION ...

typedef int (*git_remote_create_cb)(
	git_remote **out,
	git_repository *repo,
	const char *name,
	const char *url,
	void *payload);

typedef int (*git_repository_create_cb)(
	git_repository **out,
	const char *path,
	int bare,
	void *payload);

typedef enum {
	GIT_CLONE_LOCAL_AUTO,
	GIT_CLONE_LOCAL,
	GIT_CLONE_NO_LOCAL,
	GIT_CLONE_LOCAL_NO_LINKS,
} git_clone_local_t;

typedef struct git_clone_options {
	unsigned int version;
	git_checkout_options checkout_opts;
	git_fetch_options fetch_opts;
	int bare;
	git_clone_local_t local;
	const char* checkout_branch;
	git_repository_create_cb repository_cb;
	void *repository_cb_payload;
	git_remote_create_cb remote_cb;
	void *remote_cb_payload;
} git_clone_options;

int git_clone_options_init(
	git_clone_options *opts,
	unsigned int version);

int git_clone(
	git_repository **out,
	const char *url,
	const char *local_path,
	const git_clone_options *options);
