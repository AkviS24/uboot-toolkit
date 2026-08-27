"""Tests for binary structure parsers."""

import pytest

from uboot_toolkit.parser import parse_dtb_header

def test_parse_dtb_header() -> None:
    """Parse a valid DTB header."""
    data = bytes.fromhex(
        "D00DFEED"
        "00000A00"
        "00000048"
        "00000808"
        "00000028"
        "00000011"
        "00000010"
        "00000000"
        "000000CD"
        "000007C0"
    )

    header = parse_dtb_header(data)

    assert header.magic == 0xD00DFEED
    assert header.total_size == 2560
    assert header.structure_offset == 0x48
    assert header.strings_offset == 0x808
    assert header.memory_reservation_offset == 0x28
    assert header.version == 17
    assert header.last_compatible_version == 16
    assert header.boot_cpu_id == 0
    assert header.structure_size == 1984
    assert header.strings_size == 205


def test_parse_dtb_header_at_offset() -> None:
    """Parse a DTB header at a non-zero offset."""
    header_data = bytes.fromhex(
        "D00DFEED"
        "00000A00"
        "00000048"
        "00000808"
        "00000028"
        "00000011"
        "00000010"
        "00000000"
        "000000CD"
        "000007C0"
    )

    data = b"\x00" * 10 + header_data

    header = parse_dtb_header(data, offset=10)

    assert header.magic == 0xD00DFEED
    assert header.total_size == 2560


def test_parse_invalid_dtb_magic() -> None:
    """Reject data with an invalid DTB magic."""
    data = b"\x00" * 40

    with pytest.raises(ValueError, match="Invalid DTB magic"):
        parse_dtb_header(data)


def test_parse_incomplete_dtb_header() -> None:
    """Reject data shorter than a DTB header."""
    data = b"\xD0\x0D\xFE\xED"

    with pytest.raises(ValueError, match="Not enough data"):
        parse_dtb_header(data)

