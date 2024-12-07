import os
from pathlib import Path
from typing import AnyStr


class SeekFile:
    def __init__(self, file_path: Path | str, mode: str = 'rb+'):
        """Initialize the SeekFile object and open the file."""
        if type(file_path) == str:
            file_path = Path(file_path)
        self.file_path = file_path
        self.touch()

        self.mode = mode
        self.file = None
        self.open()

    def touch(self):
        self.file_path.touch(exist_ok = True)

    def open(self):
        self.touch()
        self.file = open(self.file_path, self.mode)

    def seek(self, offset: int, whence: int = 0):
        """Move the file pointer to the specified offset. By default, from the beginning."""
        self.file.seek(offset, whence)

    def seek_to_end(self):
        """Move the file pointer to the end of the file."""
        self.seek(0, os.SEEK_END)

    def read(self, num_bytes: int) -> AnyStr:
        """Read a specified number of bytes from the current file pointer position."""
        return self.file.read(num_bytes)

    def read_all_from_offset(self, offset: int) -> AnyStr:
        """Read all data from the specified offset to the end of the file."""
        self.seek(offset)
        return self.file.read()

    def write(self, data: AnyStr):
        """Write data at the current file pointer position."""
        self.file.write(data)

    def write_at_offset(self, offset: int, data: AnyStr):
        """Write data at a specified offset."""
        self.seek(offset)
        self.write(data)

    def get_position(self) -> int:
        """Get current position"""
        return self.file.tell()

    def close(self):
        """Close the file."""
        self.file.close()

    def delete(self):
        self.file_path.unlink(missing_ok = True)
        self.close()

    def __del__(self):
        """Ensure the file is closed when the object is deleted."""
        self.close()
