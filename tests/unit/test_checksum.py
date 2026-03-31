from pathlib import Path

from newspace_twin.registry.checksum import sha256_file


def test_sha256_file(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("abc", encoding="utf-8")
    assert len(sha256_file(sample)) == 64
