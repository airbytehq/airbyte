typedef int (*git_packbuilder_progress)(
	int stage,
	uint32_t current,
	uint32_t total,
	void *payload);

int git_packbuilder_new(git_packbuilder **out, git_repository *repo);
void git_packbuilder_free(git_packbuilder *pb);

int git_packbuilder_insert(git_packbuilder *pb, const git_oid *id, const char *name);
int git_packbuilder_insert_recur(git_packbuilder *pb, const git_oid *id, const char *name);

size_t git_packbuilder_object_count(git_packbuilder *pb);

int git_packbuilder_write(git_packbuilder *pb, const char *path, unsigned int mode, git_indexer_progress_cb progress_cb, void *progress_cb_payload);
uint32_t git_packbuilder_written(git_packbuilder *pb);

unsigned int git_packbuilder_set_threads(git_packbuilder *pb, unsigned int n);
