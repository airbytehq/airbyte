package io.airbyte.cdk.core.config.annotation

import java.lang.annotation.Documented

@Target(AnnotationTarget.ANNOTATION_CLASS, AnnotationTarget.FIELD, AnnotationTarget.FUNCTION, AnnotationTarget.VALUE_PARAMETER)
@Retention(AnnotationRetention.RUNTIME)
@Documented
annotation class AirbyteDisplayHint(
    val alwaysShow:Boolean = false,
    val description:String = "",
    val enum:Array<String> = [],
    val examples:Array<String> = [],
    val order:Int = 0,
    val secret:Boolean = false,
    val title:String = "",
)
