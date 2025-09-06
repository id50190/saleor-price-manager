#!/usr/bin/bash

set -e

# [[ `uname` != 'Linux' ]] && echo 'The script needs to be run on Linux.' && exit 1

# if [[ $UID -ne 0 ]]; then
#   echo "The script needs to be run with root rights. Running with sudo..."
#   sudo "$0"; exit $?
# fi

# cmds=(python3 pip bc); for cmd in "${cmds[@]}"; do
#   if ! command -v "$cmd" &>/dev/null; then
#     echo "Error: Command \`$cmd\` not found in your \`PATH\` environment variable."
#     echo "Please make sure \`$cmd\` is installed and available in your \`PATH\`."
#     exit 1
#   fi
# done

# MINIMAL_PYTHON_VERSION='3.11'
# current_python_version="$(python3 -c 'import sys; print(sys.version_info.major + sys.version_info.minor/100)' 2>/dev/null)" 2>/dev/null # Get Python version
# if [[ -z "$current_python_version" ]]; then # Check if version retrieval was successful
#   echo "Error: Failed to determine Python version. Ensure python3 is installed and accessible."
#   exit 1
# fi
# if (( ! $(echo "$current_python_version >= $MINIMAL_PYTHON_VERSION" | bc) )); then # if [[ $(printf '%s\n' "$current_python_version" "3.12" | sort -V | head -n 1) == "3.12" ]]; then
#   echo "Error: Python version $MINIMAL_PYTHON_VERSION or higher is required."
#   exit 1
# fi

# PREUSED_PYTHON_VERSION='Python 3.13.2'
# current_python_version="$(python3 --version)"
# if [[ ! "$current_python_version" == "$PREUSED_PYTHON_VERSION" ]]; then
#   echo "Warning! The current version \`$(python3 --version)}\` does not correspond to the version used during development: (\`$PREUSED_PYTHON_VERSION\`)."
#   exit 1
# fi