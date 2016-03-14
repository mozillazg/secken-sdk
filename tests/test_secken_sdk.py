#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_secken_sdk
----------------------------------

Tests for `secken_sdk` module.
"""

import pytest

from secken_sdk import Secken


@pytest.yield_fixture
def secken():
    yield Secken()


class TestSecken:

    def test_000_something(self, secken):
        pass
