# TODO: Use an actual build system like CMakeLists
CURRENT_DIR="$(pwd)"
SCRIPT_DIR="$(dirname -- "$(readlink -f "${BASH_SOURCE}")")"
cd "${SCRIPT_DIR}/led_driver/"
bash build.sh
cd "${SCRIPT_DIR}/button_monitor/"
bash build.sh

cd "${CURRENT_DIR}"