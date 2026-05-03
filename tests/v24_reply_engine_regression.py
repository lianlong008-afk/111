#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression checks for V24 reply generation fallback and parsing."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pickup_master_v24 import MiniMaxAPI, PickupMasterV24


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


def check_no_api_key_chat_is_usable() -> None:
    master = PickupMasterV24(api_key="")
    session_id = master.start_session("regression")
    result = master.chat("在干嘛呢", girl_name="小美")

    assert_equal(result["session_id"], session_id, "chat should keep current session")
    assert_equal(len(result["options"]), 3, "chat should always expose three options")
    assert_true("本地兜底" in result["info"], "missing API key should use local fallback")
    assert_true("API Key" not in result["reply"], "chat reply should not expose setup errors")
    assert_true(result["reply"], "chat reply should not be empty")


def check_api_response_parser_cleans_common_formatting() -> None:
    content = """
    1. "刚忙完就看到你啦"
    2、我也正想找你呢
    - 你一出现就不忙了
    """
    replies = MiniMaxAPI._parse_replies(content)

    assert_equal(replies, ["刚忙完就看到你啦", "我也正想找你呢", "你一出现就不忙了"], "parser cleanup")


def check_api_response_parser_fills_short_outputs() -> None:
    replies = MiniMaxAPI._parse_replies("1. 好呀")

    assert_equal(len(replies), 3, "parser should fill fallback replies")
    assert_equal(replies[0], "好呀", "parser should keep valid short reply")


def main() -> None:
    check_no_api_key_chat_is_usable()
    check_api_response_parser_cleans_common_formatting()
    check_api_response_parser_fills_short_outputs()


if __name__ == "__main__":
    main()
