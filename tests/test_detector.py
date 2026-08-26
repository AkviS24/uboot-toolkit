"""Tests for the binary signature detector"""

from uboot_toolkit.detector import detect_signatures

def test_detect_dtb_signature() -> None:
    """Detect a DTB signature in binary data."""
    data = b"\x00\x00\xd0\x0d\xfe\xed\x00\x00"

    detections = detect_signatures(data)

    assert len(detections) == 1
    assert detections[0].name == "Device Tree Blob (DTB)"
    assert detections[0].offset == 2
    assert detections[0].signature == b"\xd0\x0d\xfe\xed"


def test_detect_multiple_dtb_signatures() -> None:
    """Detect multiple DTB signatures."""
    signature = b"\xd0\x0d\xfe\xed"
    data = signature + b"\x00" * 10 + signature

    detections = detect_signatures(data)

    assert len(detections) == 2
    assert detections[0].offset == 0
    assert detections[1].offset == 14


def test_detect_no_known_signature() -> None:
    """Return no detections for unknown data."""
    data = b"\x00" * 100

    detections = detect_signatures(data)

    assert detections == []