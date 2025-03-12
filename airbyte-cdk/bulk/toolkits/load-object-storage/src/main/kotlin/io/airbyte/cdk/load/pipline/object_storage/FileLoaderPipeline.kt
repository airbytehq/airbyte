package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.write.object_storage.FileLoader
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(bean = FileLoader::class)
@Replaces(ObjectLoaderPipeline::class)
class FileLoaderPipeline(
    partStep: FileLoaderPartStep,
    uploadStep: ObjectLoaderUploadStep
): LoadPipeline(
    listOf(partStep, uploadStep)
)
