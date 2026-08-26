"""Binary signature detection for firmware images."""

from dataclasses import dataclass

@dataclass(frozen=True)
class Detection:

    name: str
    offset: int
    signature: bytes

SIGNATURES = {
    "Device Tree Blob (DTB)": b"\xd0\x0d\xfe\xed",
}


def detect_signatures(data: bytes) -> list[Detection]:
    """Find known binary signatures in image data"""
    detections = []

    for name, signature in SIGNATURES.items():
        start = 0

        while True:
            offset = data.find(signature, start)

            if offset == -1:
                break

            detections.append(
                Detection(
                    name=name,
                    offset=offset,
                    signature=signature,
                )
            )
            start = offset + 1
    return detections