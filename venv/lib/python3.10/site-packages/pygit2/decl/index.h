typedef struct {
	int32_t seconds;
	uint32_t nanoseconds;
} git_index_time;

typedef struct git_index_entry {
	git_index_time ctime;
	git_index_time mtime;

	uint32_t dev;
	uint32_t ino;
	uint32_t mode;
	uint32_t uid;
	uint32_t gid;
	uint32_t file_size;

	git_oid id;

	uint16_t flags;
	uint16_t flags_extended;

	const char *path;
} git_index_entry;

typedef int (*git_index_matched_path_cb)(
	const char *path, const char *matched_pathspec, void *payload);

void git_index_free(git_index *index);
int git_index_open(git_index **out, const char *index_path);
int git_index_read(git_index *index, int force);
int git_index_write(git_index *index);
size_t git_index_entrycount(const git_index *index);
int git_index_find(size_t *at_pos, git_index *index, const char *path);
int git_index_add_bypath(git_index *index, const char *path);
int git_index_add(git_index *index, const git_index_entry *source_entry);
int git_index_remove(git_index *index, const char *path, int stage);
int git_index_read_tree(git_index *index, const git_tree *tree);
int git_index_clear(git_index *index);
int git_index_write_tree(git_oid *out, git_index *index);
int git_index_write_tree_to(git_oid *out, git_index *index, git_repository *repo);
const git_index_entry * git_index_get_bypath(
	git_index *index, const char *path, int stage);
const git_index_entry * git_index_get_byindex(
	git_index *index, size_t n);
int git_index_add_all(
	git_index *index,
	const git_strarray *pathspec,
	unsigned int flags,
	git_index_matched_path_cb callback,
	void *payload);
int git_index_remove_all(
	git_index *index,
	const git_strarray *pathspec,
	git_index_matched_path_cb callback,
	void *payload);
int git_index_has_conflicts(const git_index *index);
void git_index_conflict_iterator_free(
	git_index_conflict_iterator *iterator);
int git_index_conflict_iterator_new(
	git_index_conflict_iterator **iterator_out,
	git_index *index);
int git_index_conflict_get(
	const git_index_entry **ancestor_out,
	const git_index_entry **our_out,
	const git_index_entry **their_out,
	git_index *index,
	const char *path);

int git_index_conflict_next(
	const git_index_entry **ancestor_out,
	const git_index_entry **our_out,
	const git_index_entry **their_out,
	git_index_conflict_iterator *iterator);
int git_index_conflict_remove(git_index *index, const char *path);
