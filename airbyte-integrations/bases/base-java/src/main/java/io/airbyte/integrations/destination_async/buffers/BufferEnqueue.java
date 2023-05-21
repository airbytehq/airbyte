package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;

import java.util.concurrent.ConcurrentMap;

public class BufferEnqueue {

    public static final long BLOCK_SIZE_BYTES = 10 * 1024 * 1024;
    public static final long INITIAL_QUEUE_SIZE_BYTES = BLOCK_SIZE_BYTES;
    public static final long MAX_CONCURRENT_QUEUES = 10L;


    private final RecordSizeEstimator recordSizeEstimator;

    private final GlobalMemoryManager memoryManager;
    private final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

    public BufferEnqueue(final GlobalMemoryManager memoryManager,
                         final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
        this.memoryManager = memoryManager;
        this.buffers = buffers;
        recordSizeEstimator = new RecordSizeEstimator();
    }

    public void addRecord(final StreamDescriptor streamDescriptor, final AirbyteMessage message) {
        if (!buffers.containsKey(streamDescriptor)) {
            buffers.put(streamDescriptor, new MemoryBoundedLinkedBlockingQueue<>(INITIAL_QUEUE_SIZE_BYTES));
        }

        // todo (cgardens) - handle estimating state message size.
        final long messageSize = message.getType() == AirbyteMessage.Type.RECORD ? recordSizeEstimator.getEstimatedByteSize(message.getRecord()) : 1024;

        final var queue = buffers.get(streamDescriptor);
        var addedToQueue = queue.offer(message, messageSize);

        // todo (cgardens) - what if the record being added is bigger than the block size?
        // if failed, try to increase memory and add to queue.
        while (!addedToQueue) {
            final var freeMem = memoryManager.requestMemory();
            if (freeMem > 0) {
                queue.setMaxMemoryUsage(queue.getMaxMemoryUsage() + freeMem);
            }
            addedToQueue = queue.offer(message, messageSize);
        }
    }

}
