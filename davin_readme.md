Looking at [ConfigRepository.java](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/persistence/src/main/java/io/airbyte/config/persistence/ConfigRepository.java#L527) it looks like the pointer has moved some.  I assume the method we want here is `writeSourceConnectionNoSecret` now located at [ConfigRepository.java:536](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/persistence/src/main/java/io/airbyte/config/persistence/ConfigRepository.java#L536)

When I look here it looks like a bit like magic to me.  I was confused by this at first reading leading to alot of my lost effort below.  I was expecting to impliment double write in here, but `getTimeToWait` seems like read only logic.  I still don't see where i can write the logic to double write scheduleType and schedule

I command clicked my way from there to the [StandardSync.yaml](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/models/src/main/resources/types/StandardSync.yaml).  I added tims yaml there

Looking at [configfetch](https://github.com/airbytehq/airbyte/blob/master/airbyte-workers/src/main/java/io/airbyte/workers/temporal/scheduling/activities/ConfigFetchActivityImpl.java#L34) My first question to myself is how do i get inside this thing to test it.  I found the test file quickly, i'm not sure how to run this specific test though

I added the new property to StandardSync but i am unable to grok the enum for double write in this context, and i don't see obvious parallels at the moment

I don't understand what `StandardSyncInput` or output are meant to be, and in these files it's hard to tell what is generated and what isn't

Turns out i was editing generated files.  I didn't look at the folder higherarchy closely enough

looking again at [configfetch](https://github.com/airbytehq/airbyte/blob/master/airbyte-workers/src/main/java/io/airbyte/workers/temporal/scheduling/activities/ConfigFetchActivityImpl.java#L36) I know that i want to double write, but the strict typing here has me confused

Looked up how to use gradle tasks to list known tasks. Some questions:
Why do we wrap gradle in the local `./gradlew`
double you tee eff is this `./gradlew knows`
not understanding that i could run `./gradlew tasks` earlier makes me feel silly


Getting stuck on enum use [tried this article](https://www.baeldung.com/a-guide-to-java-enums)
