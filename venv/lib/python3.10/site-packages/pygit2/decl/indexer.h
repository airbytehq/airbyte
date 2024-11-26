typedef struct git_indexer_progress {
	unsigned int total_objects;
	unsigned int indexed_objects;
	unsigned int received_objects;
	unsigned int local_objects;
	unsigned int total_deltas;
	unsigned int indexed_deltas;
	size_t received_bytes;
} git_indexer_progress;

typedef int (*git_indexer_progress_cb)(const git_indexer_progress *stats, void *payload);
