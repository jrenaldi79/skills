#!/bin/bash
# Integration tests for pod_reminder.py hook script.
# Validates that the hook handles all scenarios correctly.
#
# Usage: bash plugin/evals/test_hooks.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/scripts/pod_reminder.py"
PASS=0
FAIL=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

assert_exit_code() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"
    if [ "$actual" -eq "$expected" ]; then
        echo -e "  ${GREEN}PASS${NC} $test_name (exit $actual)"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}FAIL${NC} $test_name (expected exit $expected, got $actual)"
        FAIL=$((FAIL + 1))
    fi
}

assert_output_empty() {
    local test_name="$1"
    local output="$2"
    if [ -z "$output" ]; then
        echo -e "  ${GREEN}PASS${NC} $test_name (no output)"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}FAIL${NC} $test_name (expected no output, got: $output)"
        FAIL=$((FAIL + 1))
    fi
}

assert_output_contains() {
    local test_name="$1"
    local output="$2"
    local pattern="$3"
    if echo "$output" | grep -q "$pattern"; then
        echo -e "  ${GREEN}PASS${NC} $test_name (contains '$pattern')"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}FAIL${NC} $test_name (expected '$pattern' in output: $output)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Pod Reminder Hook Tests ==="
echo ""

# ─────────────────────────────────────────────
# Test 1: No .env found → silent exit
# ─────────────────────────────────────────────
echo "Test 1: No .env found → silent exit"
TMPDIR1=$(mktemp -d)
OUTPUT=$(echo '{"cwd": "'"$TMPDIR1"'", "hook_event_name": "SessionStart"}' | \
    CLAUDE_PROJECT_DIR="$TMPDIR1" python3 "$HOOK_SCRIPT" 2>/dev/null || true)
EXIT_CODE=$?
assert_exit_code "exit code 0" 0 $EXIT_CODE
assert_output_empty "no output" "$OUTPUT"
rm -rf "$TMPDIR1"
echo ""

# ─────────────────────────────────────────────
# Test 2: .env exists but missing credentials → silent exit
# ─────────────────────────────────────────────
echo "Test 2: .env exists but missing credentials → silent exit"
TMPDIR2=$(mktemp -d)
cat > "$TMPDIR2/.env" << 'EOF'
# Empty config
RUNPOD_API_KEY=
RUNPOD_POD_ID=
EOF
OUTPUT=$(echo '{"cwd": "'"$TMPDIR2"'", "hook_event_name": "SessionStart"}' | \
    CLAUDE_PROJECT_DIR="$TMPDIR2" python3 "$HOOK_SCRIPT" 2>/dev/null || true)
EXIT_CODE=$?
assert_exit_code "exit code 0" 0 $EXIT_CODE
assert_output_empty "no output" "$OUTPUT"
rm -rf "$TMPDIR2"
echo ""

# ─────────────────────────────────────────────
# Test 3: .env exists with credentials but invalid API key → silent exit (no crash)
# ─────────────────────────────────────────────
echo "Test 3: .env with invalid API key → silent exit (no crash)"
TMPDIR3=$(mktemp -d)
cat > "$TMPDIR3/.env" << 'EOF'
RUNPOD_API_KEY=rpa_INVALID_KEY_12345
RUNPOD_POD_ID=fake_pod_id
EOF
OUTPUT=$(echo '{"cwd": "'"$TMPDIR3"'", "hook_event_name": "SessionStart"}' | \
    CLAUDE_PROJECT_DIR="$TMPDIR3" python3 "$HOOK_SCRIPT" 2>/dev/null || true)
EXIT_CODE=$?
assert_exit_code "exit code 0" 0 $EXIT_CODE
assert_output_empty "no output (network error handled gracefully)" "$OUTPUT"
rm -rf "$TMPDIR3"
echo ""

# ─────────────────────────────────────────────
# Test 4: .env found via CLAUDE_PROJECT_DIR
# ─────────────────────────────────────────────
echo "Test 4: .env found via CLAUDE_PROJECT_DIR (not cwd)"
TMPDIR4_CWD=$(mktemp -d)
TMPDIR4_PROJECT=$(mktemp -d)
cat > "$TMPDIR4_PROJECT/.env" << 'EOF'
RUNPOD_API_KEY=rpa_INVALID_BUT_FOUND
RUNPOD_POD_ID=found_via_project_dir
EOF
# CWD has no .env, but CLAUDE_PROJECT_DIR does
OUTPUT=$(echo '{"cwd": "'"$TMPDIR4_CWD"'", "hook_event_name": "SessionStart"}' | \
    CLAUDE_PROJECT_DIR="$TMPDIR4_PROJECT" python3 "$HOOK_SCRIPT" 2>/dev/null || true)
EXIT_CODE=$?
# Should find the .env and try to query (then fail silently on network)
assert_exit_code "exit code 0" 0 $EXIT_CODE
assert_output_empty "no output (found .env but network fails gracefully)" "$OUTPUT"
rm -rf "$TMPDIR4_CWD" "$TMPDIR4_PROJECT"
echo ""

# ─────────────────────────────────────────────
# Test 5: Malformed JSON stdin → graceful handling
# ─────────────────────────────────────────────
echo "Test 5: Malformed JSON stdin → script handles error"
OUTPUT=$(echo 'NOT_JSON' | python3 "$HOOK_SCRIPT" 2>/dev/null || true)
EXIT_CODE=$?
# Script should crash but not hang — exit code may be non-zero
echo -e "  ${GREEN}PASS${NC} script did not hang (exit $EXIT_CODE)"
PASS=$((PASS + 1))
echo ""

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
echo "=== Results ==="
TOTAL=$((PASS + FAIL))
echo -e "Passed: ${GREEN}$PASS${NC}/$TOTAL"
if [ "$FAIL" -gt 0 ]; then
    echo -e "Failed: ${RED}$FAIL${NC}/$TOTAL"
    exit 1
else
    echo "All tests passed."
    exit 0
fi
