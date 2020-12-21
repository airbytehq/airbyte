import org.apache.tools.ant.taskdefs.condition.Os

class CrossPlatformSupport {
    /**
     *
     * @param args The full command to be executed split into array. This is typically the input to `commandLine` in
     * the exec task.
     */
    static formatCmd(Object... cmdParts){
        List<Object> formattedParts = []
        if (Os.isFamily(Os.FAMILY_WINDOWS)) {
            formattedParts.addAll(['cmd', '/c'])
        }

        formattedParts.addAll(cmdParts)

        return formattedParts.toArray()
    }
}
