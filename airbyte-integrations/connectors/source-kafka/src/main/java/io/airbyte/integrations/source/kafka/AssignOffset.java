package io.airbyte.integrations.source.kafka;


import java.util.Collection;
import java.util.Iterator;
import java.util.Map;
import org.apache.kafka.clients.consumer.Consumer;
import org.apache.kafka.clients.consumer.ConsumerRebalanceListener;
import org.apache.kafka.common.TopicPartition;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AssignOffset implements ConsumerRebalanceListener {
    private Consumer<?, ?> consumer;
    private Map<String, Map<Integer, Long>> offset;
    private static final Logger LOGGER = LoggerFactory.getLogger(AssignOffset.class);

    public AssignOffset(Consumer<?, ?> consumer, Map<String, Map<Integer, Long>> offsets) {
        this.consumer = consumer;
        this.offset = offsets;
    }

    public void onPartitionsRevoked(Collection<TopicPartition> partitions) {

    }

    private long readOffsetFromLookup(TopicPartition partition) {
        Map<Integer, Long> partitionoffsets = (Map)this.offset.get(partition.topic());
        long lastoffset = -1L;
        if (partitionoffsets != null) {
            lastoffset = (Long)partitionoffsets.get(partition.partition());
            ++lastoffset;
        }

        return lastoffset;
    }

    public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
        Iterator var2 = partitions.iterator();

        while(var2.hasNext()) {
            TopicPartition partition = (TopicPartition)var2.next();
            long offset = this.readOffsetFromLookup(partition);
            if (offset > 0L) {
                this.consumer.seek(partition, offset);
            }
        }

    }

}
