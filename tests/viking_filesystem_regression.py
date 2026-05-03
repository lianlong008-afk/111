#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression checks for Viking file-system persistence."""

from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pickup_master_v22_viking import PickupMasterViking
from pickup_master_v23_ultimate import PickupMasterV23


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


def check_v22_idempotency(tmp_dir: str) -> None:
    first = PickupMasterViking(storage_path=tmp_dir)
    first_count = first.status()["total_nodes"]

    second = PickupMasterViking(storage_path=tmp_dir)
    second_count = second.status()["total_nodes"]

    assert_equal(second_count, first_count, "V22 static resource initialization must be idempotent")
    assert_equal(len(second.fs.list_directory("resources")), 3, "V22 resources directory count")
    assert_equal(len(second.fs.list_directory("skills")), 2, "V22 skills directory count")

    second.start_session("regression")
    second.add_memory("小美", "第一次记忆")
    second.add_memory("小美", "第二次记忆")
    memories = second.fs.list_directory("memory")
    assert_equal(len(memories), 2, "V22 memory nodes should append, not overwrite")
    assert_equal(len({node.uri for node in memories}), 2, "V22 memory URIs should be unique")


def check_v23_idempotency(tmp_dir: str) -> None:
    first = PickupMasterV23(storage_path=tmp_dir)
    first_count = first.status()["total_nodes"]

    second = PickupMasterV23(storage_path=tmp_dir)
    second_count = second.status()["total_nodes"]

    assert_equal(second_count, first_count, "V23 static technique initialization must be idempotent")
    assert_equal(len(second.fs.list_directory("techniques")), 14, "V23 techniques directory count")
    assert_equal(len(second.fs.list_directory("resources")), 2, "V23 resources directory count")
    assert_true(second.fs.get_node("viking://techniques/opening_lines"), "V23 named technique URI lookup")

    second.start_session("regression")
    second.add_memory("小美", "第一次记忆")
    second.add_memory("小美", "第二次记忆")
    memories = second.fs.list_directory("memory")
    assert_equal(len(memories), 2, "V23 memory nodes should append, not overwrite")
    assert_equal(len({node.uri for node in memories}), 2, "V23 memory URIs should be unique")


def main() -> None:
    base_dir = tempfile.mkdtemp(prefix="viking_fs_regression_")
    try:
        check_v22_idempotency(str(Path(base_dir) / "v22"))
        check_v23_idempotency(str(Path(base_dir) / "v23"))
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
