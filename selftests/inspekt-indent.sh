#!/bin/sh -e
# Skip checking test_utils_cpu.py due to inspektor bug
inspekt indent --exclude=.git,selftests/unit/test_utils_cpu.py
