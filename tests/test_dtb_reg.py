from uboot_toolkit.decoder import decode_reg


def test_decode_reg_with_one_address_and_one_size_cell() -> None:
    """Decode a reg property with one address and one size cell."""

    value = (
        b"\x00\x00\x00\x10"  # address = 0x10
        b"\x00\x00\x00\x20"  # size = 0x20
    )

    result = decode_reg(
        value=value,
        address_cells=1,
        size_cells=1,
    )

    assert result == [
        {
            "address": 0x10,
            "size": 0x20,
        }
    ]


def test_decode_reg_with_two_address_cells() -> None:
    """Decode a reg property with a 64-bit address."""

    value = (
        b"\x00\x00\x00\x00"
        b"\xFE\x01\x00\x00"
        b"\x00\x00\x00\x00"
        b"\x00\x00\x10\x00"
    )

    result = decode_reg(
        value=value,
        address_cells=2,
        size_cells=2,
    )

    assert result == [
        {
            "address": 0xFE010000,
            "size": 0x1000,
        }
    ]


def test_decode_reg_with_multiple_entries() -> None:
    """Decode multiple address/size entries."""

    value = (
        b"\x00\x00\x10\x00"
        b"\x00\x00\x01\x00"
        b"\x00\x00\x20\x00"
        b"\x00\x00\x02\x00"
    )

    result = decode_reg(
        value=value,
        address_cells=1,
        size_cells=1,
    )

    assert result == [
        {
            "address": 0x1000,
            "size": 0x100,
        },
        {
            "address": 0x2000,
            "size": 0x200,
        },
    ]