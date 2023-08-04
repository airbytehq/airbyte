printf "Docker ";
if [[ $(which docker) && $(docker --version) ]]; then
    printf "is installed"
  else
    printf "needs to be installed"
fi;
printf "\n";
desired="14"
printf "Java ";
if [[ "$(which java)" && "$(java --version)" ]]; 
    then
        printf "installed"
        str="$(java --version)"
        IFS=' ' read -ra array <<< "${str}"
        version="${array[1]}"
        if [[ "${version}" > "${desired}" || "${version}" == "${desired}" ]];
            then
                printf " and functional"
            else
                printf " but not functional, must have version ${desired} at least"
        fi
    else
        printf "not installed, must have version ${desired} at least"
fi;
printf "\n";
desired="20.1"
printf "Pip ";
if [[ "$(which pip)" && "$(pip --version)" ]]; 
    then
        printf "installed"
        str="$(pip --version)"
        IFS=' ' read -ra array <<< "${str}"
        version="${array[1]}"
        if [[ "${version}" > "${desired}" || "${version}" == "${desired}" ]];
            then
                printf " and functional"
            else
                printf " but not functional, must have version ${desired} at least"
        fi
    else
        printf "not installed, must have version ${desired} at least"
fi;
printf "\n";
desired="3.9.11"
printf "Python ";
if [[ "$(which python3)" && "$(python3 --version)" ]]; 
    then
        printf "installed"
        str="$(python3 --version)"
        IFS=' ' read -ra array <<< "${str}"
        version="${array[1]}"
        if [[ "${version}" > "${desired}" || "${version}" == "${desired}" ]];
            then
                printf " and functional"
            else
                printf " but not functional, must have version ${desired} at least"
        fi
    else
        printf "not installed, must have version ${desired} at least"
fi;
printf "\n";
printf "JQ ";
if [[ $(which jq) && $(jq --version) ]]; then
    printf "is installed"
  else
    printf "needs to be installed"
fi;
printf "\n";