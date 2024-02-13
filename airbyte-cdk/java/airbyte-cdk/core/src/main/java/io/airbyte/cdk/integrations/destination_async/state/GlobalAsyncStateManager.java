/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.state;

import static java.lang.Thread.sleep;

import com.google.common.base.Preconditions;
import com.google.common.base.Strings;
import io.airbyte.cdk.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.LinkedBlockingDeque;
import java.util.concurrent.atomic.AtomicLong;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.mina.util.ConcurrentHashSet;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Responsible for managing state within the Destination. The general approach is a ref counter
 * approach - each state message is associated with a record count. This count represents the number
 * of preceding records. For a state to be emitted, all preceding records have to be written to the
 * destination i.e. the counter is 0.
 * <p>
 * A per-stream state queue is maintained internally, with each state within the queue having a
 * counter. This means we *ALLOW* records succeeding an unemitted state to be written. This
 * decouples record writing from state management at the cost of potentially repeating work if an
 * upstream state is never written.
 * <p>
 * One important detail here is the difference between how PER-STREAM & NON-PER-STREAM is handled.
 * The PER-STREAM case is simple, and is as described above. The NON-PER-STREAM case is slightly
 * tricky. Because we don't know the stream type to begin with, we always assume PER_STREAM until
 * the first state message arrives. If this state message is a GLOBAL state, we alias all existing
 * state ids to a single global state id via a set of alias ids. From then onwards, we use one id -
 * {@link #SENTINEL_GLOBAL_DESC} regardless of stream. Read
 * {@link #convertToGlobalIfNeeded(AirbyteMessage)} for more detail.
 */
@Slf4j
public class GlobalAsyncStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(GlobalAsyncStateManager.class);

  private static final StreamDescriptor SENTINEL_GLOBAL_DESC = new StreamDescriptor().withName(UUID.randomUUID().toString());
  private final GlobalMemoryManager memoryManager;

  /**
   * Memory that the manager has allocated to it to use. It can ask for more memory as needed.
   */
  private final AtomicLong memoryAllocated;
  /**
   * Memory that the manager is currently using.
   */
  private final AtomicLong memoryUsed;

  private boolean preState = true;
  private final ConcurrentMap<StreamDescriptor, LinkedBlockingDeque<Long>> descToStateIdQ = new ConcurrentHashMap<>();
  /**
   * Both {@link stateIdToCounter} and {@link stateIdToCounterForPopulatingDestinationStats} are used
   * to maintain a counter for the number of records associated with a give state i.e. before a state
   * was received, how many records were seen until that point. As records are received the value for
   * both are incremented. The difference is the purpose of the two attributes.
   * {@link stateIdToCounter} is used to determine whether a state is safe to emit or not. This is
   * done by decrementing the value as records are committed to the destination. If the value hits 0,
   * it means all the records associated with a given state have been committed to the destination, it
   * is safe to emit the state back to platform. But because of this we can't use it to determine the
   * actual number of records that are associated with a state to update the value of
   * {@link AirbyteStateMessage#destinationStats} at the time of emitting the state message. That's
   * where we need {@link stateIdToCounterForPopulatingDestinationStats}, which is only reset when a
   * state message has been emitted.
   */
  private final ConcurrentMap<Long, AtomicLong> stateIdToCounter = new ConcurrentHashMap<>();
  private final ConcurrentMap<Long, AtomicLong> stateIdToCounterForPopulatingDestinationStats = new ConcurrentHashMap<>();
  private final ConcurrentMap<Long, ImmutablePair<StateMessageWithArrivalNumber, Long>> stateIdToState = new ConcurrentHashMap<>();

  // Alias-ing only exists in the non-STREAM case where we have to convert existing state ids to one
  // single global id.
  // This only happens once.
  private final Set<Long> aliasIds = new ConcurrentHashSet<>();
  private long retroactiveGlobalStateId = 0;
  // All access to this field MUST be guarded by a synchronized(lock) block
  private long arrivalNumber = 0;

  private final Object LOCK = new Object();

  public GlobalAsyncStateManager(final GlobalMemoryManager memoryManager) {
    this.memoryManager = memoryManager;
    this.memoryAllocated = new AtomicLong(memoryManager.requestMemory());
    this.memoryUsed = new AtomicLong();
  }

  // Always assume STREAM to begin, and convert only if needed. Most state is per stream anyway.
  private AirbyteStateMessage.AirbyteStateType stateType = AirbyteStateMessage.AirbyteStateType.STREAM;

  /**
   * Main method to process state messages.
   * <p>
   * The first incoming state message tells us the type of state we are dealing with. We then convert
   * internal data structures if needed.
   * <p>
   * Because state messages are a watermark, all preceding records need to be flushed before the state
   * message can be processed.
   */
  public void trackState(final PartialAirbyteMessage message, final long sizeInBytes, final String defaultNamespace) {
    if (preState) {
      convertToGlobalIfNeeded(message);
      preState = false;
    }
    // stateType should not change after a conversion.
    Preconditions.checkArgument(stateType == extractStateType(message));

    closeState(message, sizeInBytes, defaultNamespace);
  }

  /**
   * Identical to {@link #getStateId(StreamDescriptor)} except this increments the associated counter
   * by 1. Intended to be called whenever a record is ingested.
   *
   * @param streamDescriptor - stream to get stateId for.
   * @return state id
   */
  public long getStateIdAndIncrementCounter(final StreamDescriptor streamDescriptor) {
    return getStateIdAndIncrement(streamDescriptor, 1);
  }

  /**
   * Each decrement represent one written record for a state. A zero counter means there are no more
   * inflight records associated with a state and the state can be flushed.
   *
   * @param stateId reference to a state.
   * @param count to decrement.
   */
  public void decrement(final long stateId, final long count) {
    synchronized (LOCK) {
      log.trace("decrementing state id: {}, count: {}", stateId, count);
      stateIdToCounter.get(getStateAfterAlias(stateId)).addAndGet(-count);
    }
  }

  /**
   * Returns state messages with no more inflight records i.e. counter = 0 across all streams.
   * Intended to be called by {@link io.airbyte.cdk.integrations.destination_async.FlushWorkers} after
   * a worker has finished flushing its record batch.
   * <p>
   * The return list of states should be emitted back to the platform.
   *
   * @return list of state messages with no more inflight records.
   */
  public List<PartialStateWithDestinationStats> flushStates() {
    final List<PartialStateWithDestinationStats> output = new ArrayList<>();
    Long bytesFlushed = 0L;
    synchronized (LOCK) {
      for (final Map.Entry<StreamDescriptor, LinkedBlockingDeque<Long>> entry : descToStateIdQ.entrySet()) {
        // Remove all states with 0 counters.
        // Per-stream synchronized is required to make sure the state (at the head of the queue)
        // logic is applied to is the state actually removed.

        final LinkedBlockingDeque<Long> stateIdQueue = entry.getValue();
        while (true) {
          final Long oldestStateId = stateIdQueue.peek();
          // no state to flush for this stream
          if (oldestStateId == null) {
            break;
          }

          // technically possible this map hasn't been updated yet.
          // This can be if you call the flush method if there are 0 records/states
          final var oldestStateCounter = stateIdToCounter.get(oldestStateId);
          if (oldestStateCounter == null) {
            break;
          }

          final var oldestState = stateIdToState.get(oldestStateId);
          // no state to flush for this stream
          if (oldestState == null) {
            break;
          }

          final var allRecordsCommitted = oldestStateCounter.get() == 0;
          if (allRecordsCommitted) {
            final StateMessageWithArrivalNumber stateMessage = oldestState.getLeft();
            final double flushedRecordsAssociatedWithState = stateIdToCounterForPopulatingDestinationStats.get(oldestStateId).doubleValue();
            output.add(new PartialStateWithDestinationStats(stateMessage.partialAirbyteStateMessage(),
                new AirbyteStateStats().withRecordCount(flushedRecordsAssociatedWithState), stateMessage.arrivalNumber()));
            bytesFlushed += oldestState.getRight();

            // cleanup
            entry.getValue().poll();
            stateIdToState.remove(oldestStateId);
            stateIdToCounter.remove(oldestStateId);
            stateIdToCounterForPopulatingDestinationStats.remove(oldestStateId);
          } else {
            break;
          }
        }
      }
    }

    freeBytes(bytesFlushed);
    return output;
  }

  private Long getStateIdAndIncrement(final StreamDescriptor streamDescriptor, final long increment) {
    final StreamDescriptor resolvedDescriptor = stateType == AirbyteStateMessage.AirbyteStateType.STREAM ? streamDescriptor : SENTINEL_GLOBAL_DESC;
    // As concurrent collections do not guarantee data consistency when iterating, use `get` instead of
    // `containsKey`.
    if (descToStateIdQ.get(resolvedDescriptor) == null) {
      registerNewStreamDescriptor(resolvedDescriptor);
    }
    synchronized (LOCK) {
      final Long stateId = descToStateIdQ.get(resolvedDescriptor).peekLast();
      final var update = stateIdToCounter.get(stateId).addAndGet(increment);
      if (increment >= 0) {
        stateIdToCounterForPopulatingDestinationStats.get(stateId).addAndGet(increment);
      }
      log.trace("State id: {}, count: {}", stateId, update);
      return stateId;
    }
  }

  /**
   * Return the internal id of a state message. This is the id that should be used to reference a
   * state when interacting with all methods in this class.
   *
   * @param streamDescriptor - stream to get stateId for.
   * @return state id
   */
  private long getStateId(final StreamDescriptor streamDescriptor) {
    return getStateIdAndIncrement(streamDescriptor, 0);
  }

  /**
   * Pass this the number of bytes that were flushed. It will track those internally and if the
   * memoryUsed gets signficantly lower than what is allocated, then it will return it to the memory
   * manager. We don't always return to the memory manager to avoid needlessly allocating /
   * de-allocating memory rapidly over a few bytes.
   *
   * @param bytesFlushed bytes that were flushed (and should be removed from memory used).
   */
  private void freeBytes(final long bytesFlushed) {
    LOGGER.debug("Bytes flushed memory to store state message. Allocated: {}, Used: {}, Flushed: {}, % Used: {}",
        FileUtils.byteCountToDisplaySize(memoryAllocated.get()),
        FileUtils.byteCountToDisplaySize(memoryUsed.get()),
        FileUtils.byteCountToDisplaySize(bytesFlushed),
        (double) memoryUsed.get() / memoryAllocated.get());

    memoryManager.free(bytesFlushed);
    memoryAllocated.addAndGet(-bytesFlushed);
    memoryUsed.addAndGet(-bytesFlushed);
    LOGGER.debug("Returned {} of memory back to the memory manager.", FileUtils.byteCountToDisplaySize(bytesFlushed));
  }

  private void convertToGlobalIfNeeded(final PartialAirbyteMessage message) {
    // instead of checking for global or legacy, check for the inverse of stream.
    stateType = extractStateType(message);
    if (stateType != AirbyteStateMessage.AirbyteStateType.STREAM) {// alias old stream-level state ids to single global state id
      // upon conversion, all previous tracking data structures need to be cleared as we move
      // into the non-STREAM world for correctness.
      synchronized (LOCK) {
        aliasIds.addAll(descToStateIdQ.values().stream().flatMap(Collection::stream).toList());
        descToStateIdQ.clear();
        retroactiveGlobalStateId = StateIdProvider.getNextId();

        descToStateIdQ.put(SENTINEL_GLOBAL_DESC, new LinkedBlockingDeque<>());
        descToStateIdQ.get(SENTINEL_GLOBAL_DESC).add(retroactiveGlobalStateId);

        final long combinedCounter = stateIdToCounter.values()
            .stream()
            .mapToLong(AtomicLong::get)
            .sum();
        stateIdToCounter.clear();
        stateIdToCounter.put(retroactiveGlobalStateId, new AtomicLong(combinedCounter));

        final long statsCounter = stateIdToCounterForPopulatingDestinationStats.values()
            .stream()
            .mapToLong(AtomicLong::get)
            .sum();
        stateIdToCounterForPopulatingDestinationStats.clear();
        stateIdToCounterForPopulatingDestinationStats.put(retroactiveGlobalStateId, new AtomicLong(statsCounter));
      }
    }
  }

  private AirbyteStateMessage.AirbyteStateType extractStateType(final PartialAirbyteMessage message) {
    if (message.getState().getType() == null) {
      // Treated the same as GLOBAL.
      return AirbyteStateMessage.AirbyteStateType.LEGACY;
    } else {
      return message.getState().getType();
    }
  }

  /**
   * When a state message is received, 'close' the previous state to associate the existing state id
   * to the newly arrived state message. We also increment the state id in preparation for the next
   * state message.
   */
  private void closeState(final PartialAirbyteMessage message, final long sizeInBytes, final String defaultNamespace) {
    final StreamDescriptor resolvedDescriptor = extractStream(message, defaultNamespace).orElse(SENTINEL_GLOBAL_DESC);
    synchronized (LOCK) {
      log.info("State with arrival number {} received", arrivalNumber);
      stateIdToState.put(getStateId(resolvedDescriptor), ImmutablePair.of(new StateMessageWithArrivalNumber(message, arrivalNumber), sizeInBytes));
      arrivalNumber++;
    }
    registerNewStateId(resolvedDescriptor);
    allocateMemoryToState(sizeInBytes);
  }

  /**
   * Given the size of a state message, tracks how much memory the manager is using and requests
   * additional memory from the memory manager if needed.
   *
   * @param sizeInBytes size of the state message
   */
  @SuppressWarnings("BusyWait")
  private void allocateMemoryToState(final long sizeInBytes) {
    if (memoryAllocated.get() < memoryUsed.get() + sizeInBytes) {
      while (memoryAllocated.get() < memoryUsed.get() + sizeInBytes) {
        memoryAllocated.addAndGet(memoryManager.requestMemory());
        try {
          LOGGER.debug("Insufficient memory to store state message. Allocated: {}, Used: {}, Size of State Msg: {}, Needed: {}",
              FileUtils.byteCountToDisplaySize(memoryAllocated.get()),
              FileUtils.byteCountToDisplaySize(memoryUsed.get()),
              FileUtils.byteCountToDisplaySize(sizeInBytes),
              FileUtils.byteCountToDisplaySize(sizeInBytes - (memoryAllocated.get() - memoryUsed.get())));
          sleep(1000);
        } catch (final InterruptedException e) {
          throw new RuntimeException(e);
        }
      }
      LOGGER.debug(getMemoryUsageMessage());
    }
  }

  public String getMemoryUsageMessage() {
    return String.format("State Manager memory usage: Allocated: %s, Used: %s, percentage Used %f",
        FileUtils.byteCountToDisplaySize(memoryAllocated.get()),
        FileUtils.byteCountToDisplaySize(memoryUsed.get()),
        (double) memoryUsed.get() / memoryAllocated.get());
  }

  /**
   * If the user has selected the Destination Namespace as the Destination default while setting up
   * the connector, the platform sets the namespace as null in the StreamDescriptor in the
   * AirbyteMessages (both record and state messages). The destination checks that if the namespace is
   * empty or null, if yes then re-populates it with the defaultNamespace. See
   * {@link io.airbyte.cdk.integrations.destination_async.AsyncStreamConsumer#accept(String,Integer)}
   * But destination only does this for the record messages. So when state messages arrive without a
   * namespace and since the destination doesn't repopulate it with the default namespace, there is a
   * mismatch between the StreamDescriptor from record messages and state messages. That breaks the
   * logic of the state management class as {@link descToStateIdQ} needs to have consistent
   * StreamDescriptor. This is why while trying to extract the StreamDescriptor from state messages,
   * we check if the namespace is null, if yes then replace it with defaultNamespace to keep it
   * consistent with the record messages.
   */
  private static Optional<StreamDescriptor> extractStream(final PartialAirbyteMessage message, final String defaultNamespace) {
    if (message.getState().getType() != null && message.getState().getType() == AirbyteStateMessage.AirbyteStateType.STREAM) {
      final StreamDescriptor streamDescriptor = message.getState().getStream().getStreamDescriptor();
      if (Strings.isNullOrEmpty(streamDescriptor.getNamespace())) {
        return Optional.of(new StreamDescriptor().withName(streamDescriptor.getName()).withNamespace(defaultNamespace));
      }
      return Optional.of(streamDescriptor);
    }
    return Optional.empty();
  }

  private long getStateAfterAlias(final long stateId) {
    if (aliasIds.contains(stateId)) {
      return retroactiveGlobalStateId;
    } else {
      return stateId;
    }
  }

  private void registerNewStreamDescriptor(final StreamDescriptor resolvedDescriptor) {
    synchronized (LOCK) {
      descToStateIdQ.put(resolvedDescriptor, new LinkedBlockingDeque<>());
    }
    registerNewStateId(resolvedDescriptor);
  }

  private void registerNewStateId(final StreamDescriptor resolvedDescriptor) {
    final long stateId = StateIdProvider.getNextId();
    synchronized (LOCK) {
      stateIdToCounter.put(stateId, new AtomicLong(0));
      stateIdToCounterForPopulatingDestinationStats.put(stateId, new AtomicLong(0));
      descToStateIdQ.get(resolvedDescriptor).add(stateId);
    }
  }

  /**
   * Simplify internal tracking by providing a global always increasing counter for state ids.
   */
  private static class StateIdProvider {

    private static final AtomicLong pk = new AtomicLong(0);

    public static long getNextId() {
      return pk.incrementAndGet();
    }

  }

  private record StateMessageWithArrivalNumber(PartialAirbyteMessage partialAirbyteStateMessage, long arrivalNumber) {}

}
