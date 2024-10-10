#!/bin/sh
# Alternative startup script for faster login times.

export _VIRTUALENVWRAPPER_API="$_VIRTUALENVWRAPPER_API mkvirtualenv rmvirtualenv lsvirtualenv showvirtualenv workon add2virtualenv cdsitepackages cdvirtualenv lssitepackages toggleglobalsitepackages cpvirtualenv setvirtualenvproject mkproject cdproject mktmpenv wipeenv allvirtualenv"

if [ -z "$VIRTUALENVWRAPPER_SCRIPT" ]
then
    export VIRTUALENVWRAPPER_SCRIPT="$(command \which virtualenvwrapper.sh)"
fi
if [ -z "$VIRTUALENVWRAPPER_SCRIPT" ]
then
    echo "ERROR: virtualenvwrapper_lazy.sh: Could not find virtualenvwrapper.sh" 1>&2
fi

# Load the real implementation of the API from virtualenvwrapper.sh
function virtualenvwrapper_load {
    # Only source the script once.
    # We might get called multiple times, because not all of _VIRTUALENVWRAPPER_API gets
    # a real completion.
    if [ -z $VIRTUALENVWRAPPER_LAZY_LOADED ]
    then
        # NOTE: For Zsh, I have tried to unset any auto-load completion.
        #       (via `compctl + $(echo ${_VIRTUALENVWRAPPER_API})`.
        #       But this does not appear to work / triggers a crash.
        source "$VIRTUALENVWRAPPER_SCRIPT"
        VIRTUALENVWRAPPER_LAZY_LOADED=1
    fi
}

# Set up "alias" functions based on the API definition.
function virtualenvwrapper_setup_lazy_loader {
    typeset venvw_name
    for venvw_name in $(echo ${_VIRTUALENVWRAPPER_API})
    do
        eval "
function $venvw_name {
    virtualenvwrapper_load
    ${venvw_name} \"\$@\"
}
"
    done
}

# Set up completion functions to virtualenvwrapper_load
function virtualenvwrapper_setup_lazy_completion {
    if [ -n "$BASH" ] ; then
        function virtualenvwrapper_lazy_load {
            virtualenvwrapper_load
            return 124
        }
        complete -o nospace -F virtualenvwrapper_lazy_load $(echo ${_VIRTUALENVWRAPPER_API})
    elif [ -n "$ZSH_VERSION" ] ; then
        compctl -K virtualenvwrapper_load $(echo ${_VIRTUALENVWRAPPER_API})
    fi
}

virtualenvwrapper_setup_lazy_loader
# Cannot be reset in zsh to fallback to files (e.g. mkvirtualenv).
virtualenvwrapper_setup_lazy_completion

unset virtualenvwrapper_setup_lazy_loader
unset virtualenvwrapper_setup_lazy_completion
