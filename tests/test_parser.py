"""Tests for binary structure parsers."""

import pytest

from uboot_toolkit.structure import (
    FDT_BEGIN_NODE,
    FDT_PROP,
    StructureToken
)

from uboot_toolkit.parser import (
    build_dtb_property,
    get_dtb_structure_bounds,
    parse_dtb_header,
    resolve_dtb_string,
    resolve_property_name,
)

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

def test_get_dtb_structure_bounds() -> None:
    """Calculate absolute DTB structure boundaries."""
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

    start, end = get_dtb_structure_bounds(header)

    assert start == 0x48
    assert end == 0x808


def test_resolve_dtb_string() -> None:
    """Resolve a null-terminated string from the DTB strings block."""
    strings = b"compatible\x00model\x00bootargs\x00"

    data = b"\x00" * 0x20 + strings

    result = resolve_dtb_string(
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
        name_offset=0,
    )

    assert result == "compatible"


def test_resolve_dtb_string_at_offset() -> None:
    """Resolve a string using an offset inside the strings block."""
    strings = b"compatible\x00model\x00bootargs\x00"

    data = b"\x00" * 0x20 + strings

    result = resolve_dtb_string(
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
        name_offset=11,
    )

    assert result == "model"


def test_resolve_property_name() -> None:
    """Resolve a property token name from the DTB strings block."""
    strings = b"compatible\x00model\x00bootargs\x00"

    data = b"\x00" * 0x20 + strings

    token = StructureToken(
        offset=0,
        token=FDT_PROP,
        name="PROP",
        property_length=4,
        property_name_offset=0,
        property_value=b"ABCD",
    )

    result = resolve_property_name(
        token=token,
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
    )

    assert result == "compatible"


def test_build_dtb_property():
    """Convert a property token into a DtbProperty."""
    strings = b"compatible\x00model\x00"

    data = b"\x00" * 0x20 + strings

    token = StructureToken(
        offset=0,
        token=FDT_PROP,
        name="PROP",
        property_length=15,
        property_name_offset=0,
        property_value=b"rockchip,rk3566",
    )

    property_item = build_dtb_property(
        token=token,
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
    )

    assert property_item.name == "compatible"
    assert property_item.value == b"rockchip,rk3566"


def test_build_dtb_property_rejects_non_property_token():
    """Reject a token that is not an FDT property token."""
    token = StructureToken(
        offset=0,
        token=FDT_BEGIN_NODE,
        name="BEGIN_NODE",
        node_name="root",
    )

    with pytest.raises(ValueError, match="Token is not a property token"):
        build_dtb_property(
            token=token,
            data=b"",
            strings_offset=0,
            strings_size=0,
        )