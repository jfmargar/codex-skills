#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(pwd)}"
ROOT_DIR="$(cd "$ROOT_DIR" && pwd)"
FAIL_ON_DOC_DRIFT="${FAIL_ON_DOC_DRIFT:-0}"
RUN_UI_JOURNEY="${RUN_UI_JOURNEY:-1}"
SDK_ROOT_DEFAULT="$HOME/Library/Android/sdk"
ADB_BIN="${ADB_BIN:-${ANDROID_SDK_ROOT:-$SDK_ROOT_DEFAULT}/platform-tools/adb}"
PROJECT_PROBE_SCRIPT="${PROJECT_PROBE_SCRIPT:-$SCRIPT_DIR/android_project_probe.py}"
NAV_AUDIT_SCRIPT="${NAV_AUDIT_SCRIPT:-$SCRIPT_DIR/navigation_flow_audit.py}"
UI_JOURNEY_SCRIPT="${UI_JOURNEY_SCRIPT:-$SCRIPT_DIR/android_ui_journey.py}"

DETECTED_MODULE_DIR=""
DETECTED_CONNECTED_TEST_TASK=""
DETECTED_UNIT_TEST_TASK=""
DETECTED_APP_ID=""
DETECTED_MAIN_ACTIVITY=""
DETECTED_NAV_DOC=""
DETECTED_FLOWS_DOC=""
DETECTED_NAV_CODE=""
DETECTED_DESTINATION_CODE=""

if [[ -f "$PROJECT_PROBE_SCRIPT" ]] && command -v python3 >/dev/null 2>&1; then
  while IFS='=' read -r key value; do
    case "$key" in
      DETECTED_MODULE_DIR) DETECTED_MODULE_DIR="$value" ;;
      DETECTED_CONNECTED_TEST_TASK) DETECTED_CONNECTED_TEST_TASK="$value" ;;
      DETECTED_UNIT_TEST_TASK) DETECTED_UNIT_TEST_TASK="$value" ;;
      DETECTED_APP_ID) DETECTED_APP_ID="$value" ;;
      DETECTED_MAIN_ACTIVITY) DETECTED_MAIN_ACTIVITY="$value" ;;
      DETECTED_NAV_DOC) DETECTED_NAV_DOC="$value" ;;
      DETECTED_FLOWS_DOC) DETECTED_FLOWS_DOC="$value" ;;
      DETECTED_NAV_CODE) DETECTED_NAV_CODE="$value" ;;
      DETECTED_DESTINATION_CODE) DETECTED_DESTINATION_CODE="$value" ;;
    esac
  done < <(python3 "$PROJECT_PROBE_SCRIPT" --root "$ROOT_DIR")
fi

MODULE_REPORT_BASE="${DETECTED_MODULE_DIR:-$ROOT_DIR/composeApp}"
if [[ ! -d "$MODULE_REPORT_BASE" ]]; then
  MODULE_REPORT_BASE="$ROOT_DIR"
fi
REPORT_DIR="${REPORT_DIR:-$MODULE_REPORT_BASE/build/reports/autotest}"
mkdir -p "$REPORT_DIR"

CONNECTED_TEST_TASK="${CONNECTED_TEST_TASK:-$DETECTED_CONNECTED_TEST_TASK}"
UNIT_TEST_TASK="${UNIT_TEST_TASK:-$DETECTED_UNIT_TEST_TASK}"
APP_ID="${APP_ID:-$DETECTED_APP_ID}"
MAIN_ACTIVITY="${MAIN_ACTIVITY:-$DETECTED_MAIN_ACTIVITY}"

NAV_DOC="${NAV_DOC:-$DETECTED_NAV_DOC}"
FLOWS_DOC="${FLOWS_DOC:-$DETECTED_FLOWS_DOC}"
NAV_CODE="${NAV_CODE:-$DETECTED_NAV_CODE}"
DESTINATION_CODE="${DESTINATION_CODE:-$DETECTED_DESTINATION_CODE}"

if [[ ! -x "$ADB_BIN" ]]; then
  echo "ERROR: adb not found at '$ADB_BIN'. Set ADB_BIN or ANDROID_SDK_ROOT."
  exit 2
fi

if [[ ! -x "$ROOT_DIR/gradlew" ]]; then
  echo "ERROR: '$ROOT_DIR/gradlew' not found. Pass the project root as first argument."
  exit 2
fi

echo "Using adb: $ADB_BIN"
echo "Reports: $REPORT_DIR"
echo "Detected connected task: ${CONNECTED_TEST_TASK:-<none>}"
echo "Detected unit task: ${UNIT_TEST_TASK:-<none>}"
echo "Detected APP_ID: ${APP_ID:-<none>}"
echo "Detected MAIN_ACTIVITY: ${MAIN_ACTIVITY:-<none>}"

DEVICE_LIST="$("$ADB_BIN" devices | awk 'NR>1 && $2=="device" {print $1}')"
if [[ -z "$DEVICE_LIST" ]]; then
  echo "ERROR: no connected emulator/device in 'device' state."
  echo "Tip: launch an AVD and retry."
  exit 3
fi

DEVICE_ID="$(echo "$DEVICE_LIST" | head -n 1)"
echo "Using device: $DEVICE_ID"
"$ADB_BIN" -s "$DEVICE_ID" wait-for-device

overall_status=0

run_gradle_task() {
  local task="$1"
  local log_file="$2"
  local required="${3:-1}"
  if [[ -z "$task" ]]; then
    echo "SKIP: task is empty"
    return 0
  fi

  echo
  echo "== Running $task =="
  set +e
  (cd "$ROOT_DIR" && "$ROOT_DIR/gradlew" "$task" --stacktrace) >"$log_file" 2>&1
  local code=$?
  set -e
  if [[ $code -ne 0 ]]; then
    if command -v rg >/dev/null 2>&1 && rg -q "Task '.*' not found in root project" "$log_file"; then
      echo "WARN: $task not found (see $log_file)"
      return 0
    fi
    if [[ "$required" == "1" ]]; then
      echo "FAIL: $task (see $log_file)"
      overall_status=1
    else
      echo "WARN: $task failed (non-blocking, see $log_file)"
    fi
  else
    echo "OK: $task"
  fi
}

run_gradle_task "$CONNECTED_TEST_TASK" "$REPORT_DIR/connectedAndroidTest.log" 0
run_gradle_task "$UNIT_TEST_TASK" "$REPORT_DIR/test.log" 0

echo
echo "== App launch smoke test =="
"$ADB_BIN" -s "$DEVICE_ID" logcat -c
if [[ -n "$APP_ID" && -n "$MAIN_ACTIVITY" ]]; then
  set +e
  "$ADB_BIN" -s "$DEVICE_ID" shell am start -W -n "$APP_ID/$MAIN_ACTIVITY" \
    >"$REPORT_DIR/app_launch.log" 2>&1
  launch_code=$?
  set -e
  if [[ $launch_code -ne 0 ]]; then
    echo "FAIL: app launch command (see $REPORT_DIR/app_launch.log)"
    overall_status=1
  else
    echo "OK: app launch command"
  fi
else
  echo "WARN: app launch skipped (APP_ID or MAIN_ACTIVITY missing)"
fi

if [[ "$RUN_UI_JOURNEY" == "1" ]]; then
  echo
  echo "== UI journey smoke =="
  if [[ -f "$UI_JOURNEY_SCRIPT" ]] && command -v python3 >/dev/null 2>&1 && [[ -n "$APP_ID" && -n "$MAIN_ACTIVITY" ]]; then
    UI_JOURNEY_ARGS=()
    [[ -n "$NAV_DOC" ]] && UI_JOURNEY_ARGS+=(--navigation-doc "$NAV_DOC")
    [[ -n "$FLOWS_DOC" ]] && UI_JOURNEY_ARGS+=(--flows-doc "$FLOWS_DOC")
    set +e
    python3 "$UI_JOURNEY_SCRIPT" \
      --adb "$ADB_BIN" \
      --device "$DEVICE_ID" \
      --app-id "$APP_ID" \
      --main-activity "$MAIN_ACTIVITY" \
      --skip-launch \
      --output "$REPORT_DIR/ui_journey_report.md" \
      "${UI_JOURNEY_ARGS[@]}" \
      >"$REPORT_DIR/ui_journey.log" 2>&1
    ui_journey_code=$?
    set -e
    if [[ $ui_journey_code -ne 0 ]]; then
      echo "FAIL: UI journey smoke (code $ui_journey_code, see $REPORT_DIR/ui_journey_report.md)"
      overall_status=1
    else
      echo "OK: UI journey smoke (see $REPORT_DIR/ui_journey_report.md)"
    fi
  else
    echo "WARN: UI journey smoke skipped (missing python3/script or app launch metadata)"
  fi
else
  echo
  echo "== UI journey smoke =="
  echo "SKIP: RUN_UI_JOURNEY=$RUN_UI_JOURNEY"
fi

sleep 8
"$ADB_BIN" -s "$DEVICE_ID" logcat -d >"$REPORT_DIR/logcat_full.log"

if command -v rg >/dev/null 2>&1; then
  rg -n "FATAL EXCEPTION|ANR in ${APP_ID}|Process: ${APP_ID}" "$REPORT_DIR/logcat_full.log" \
    >"$REPORT_DIR/logcat_critical.log" || true
else
  grep -nE "FATAL EXCEPTION|ANR in ${APP_ID}|Process: ${APP_ID}" "$REPORT_DIR/logcat_full.log" \
    >"$REPORT_DIR/logcat_critical.log" || true
fi

if [[ -s "$REPORT_DIR/logcat_critical.log" ]]; then
  echo "FAIL: critical logcat entries detected (see $REPORT_DIR/logcat_critical.log)"
  overall_status=1
else
  echo "OK: no critical logcat patterns found"
fi

echo
echo "== Navigation docs audit =="
if [[ -f "$NAV_AUDIT_SCRIPT" ]] && command -v python3 >/dev/null 2>&1 && \
   [[ -n "$NAV_DOC" && -n "$FLOWS_DOC" && -n "$NAV_CODE" && -n "$DESTINATION_CODE" ]] && \
   [[ -f "$NAV_DOC" && -f "$FLOWS_DOC" && -f "$NAV_CODE" && -f "$DESTINATION_CODE" ]]; then
  set +e
  python3 "$NAV_AUDIT_SCRIPT" \
    --navigation-doc "$NAV_DOC" \
    --flows-doc "$FLOWS_DOC" \
    --navigation-code "$NAV_CODE" \
    --destination-code "$DESTINATION_CODE" \
    --output "$REPORT_DIR/navigation_flow_audit.md" \
    $( [[ "$FAIL_ON_DOC_DRIFT" == "1" ]] && echo "--fail-on-drift" )
  nav_audit_code=$?
  set -e
  if [[ $nav_audit_code -ne 0 ]]; then
    echo "FAIL: navigation docs audit (code $nav_audit_code, see $REPORT_DIR/navigation_flow_audit.md)"
    overall_status=1
  else
    echo "OK: navigation docs audit (see $REPORT_DIR/navigation_flow_audit.md)"
  fi
else
  echo "WARN: navigation docs audit skipped (missing docs/code files or python3/script)"
fi

echo
echo "Summary logs:"
echo "- $REPORT_DIR/connectedAndroidTest.log"
echo "- $REPORT_DIR/test.log"
echo "- $REPORT_DIR/app_launch.log"
echo "- $REPORT_DIR/ui_journey.log"
echo "- $REPORT_DIR/ui_journey_report.md"
echo "- $REPORT_DIR/logcat_critical.log"
echo "- $REPORT_DIR/navigation_flow_audit.md"

exit "$overall_status"
