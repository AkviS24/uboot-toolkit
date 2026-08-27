from uboot_toolkit.decoder import decode_dtb_property


def test_decode_string() -> None:
    """Decode a null-terminated DTB string."""
    value = b"hello\x00"

    result = decode_dtb_property(value)

    assert result == "hello"


def test_decode_string_list() -> None:
    """Decode a DTB string list."""
    value = b"rockchip,rk3568-evb\x00rockchip,rk3568\x00"

    result = decode_dtb_property(value)

    assert result == [
        "rockchip,rk3568-evb",
        "rockchip,rk3568",
    ]


def test_decode_u32() -> None:
    """Decode a single 32-bit big-endian integer."""
    value = b"\x00\x00\x00\x02"

    result = decode_dtb_property(value)

    assert result == 2


def test_decode_u32_cells() -> None:
    """Decode multiple 32-bit big-endian cells."""
    value = (
        b"\x00\x00\x00\x01"
        b"\x00\x00\x00\x02"
    )

    result = decode_dtb_property(value)

    assert result == [1, 2]


def test_decode_empty_value() -> None:
    """Decode an empty DTB property value."""
    result = decode_dtb_property(b"")

    assert result is None