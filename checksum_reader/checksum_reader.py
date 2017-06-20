import hashlib
import crcmod
from io import BufferedReader


class ChecksumReader:

    def __init__(self, *args, **kwargs):
        self._hashers = dict(crc32c=crcmod.predefined.Crc("crc-32c"),
                             sha1=hashlib.sha1(),
                             sha256=hashlib.sha256(),
                             s3_etag=S3Etag())
        self._reader = BufferedReader(*args, **kwargs)
        self.raw = self._reader.raw

    def read(self, size=None):
        chunk = self._reader.read(size)
        print("read", size, "bytes")
        if chunk:
            for hasher in self._hashers.values():
                hasher.update(chunk)
        return chunk

    def get_checksums(self):
        checksums = {}
        checksums.update({name: hasher.hexdigest() for name, hasher in self._hashers.items()})
        return checksums

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

class S3Etag:
    etag_stride = 64 * 1024 * 1024

    def __init__(self):
        self._etag_bytes = 0
        self._etag_parts = []
        self._etag_hasher = hashlib.md5()

    def update(self, chunk):
        if self._etag_bytes + len(chunk) > self.etag_stride:
            chunk_head = chunk[:self.etag_stride - self._etag_bytes]
            chunk_tail = chunk[self.etag_stride - self._etag_bytes:]
            self._etag_hasher.update(chunk_head)
            self._etag_parts.append(self._etag_hasher.digest())
            self._etag_hasher = hashlib.md5()
            self._etag_hasher.update(chunk_tail)
            self._etag_bytes = len(chunk_tail)
        else:
            self._etag_hasher.update(chunk)
            self._etag_bytes += len(chunk)

    def hexdigest(self):
        if self._etag_bytes:
            self._etag_parts.append(self._etag_hasher.digest())
            self._etag_bytes = 0
        if len(self._etag_parts) > 1:
            etag_csum = hashlib.md5(b"".join(self._etag_parts)).hexdigest()
            return '"{}-{}"'.format(etag_csum, len(self._etag_parts))
        else:
            return self._etag_hasher.hexdigest()
