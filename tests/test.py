#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals
import os, sys, unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pkg_root)

from checksumming_io import ChecksummingBufferedReader

class TestChecksummingBufferedReader(unittest.TestCase):

    FILE_TO_DIGEST = 'tests/lorem_ipsum.json'
    SHA1_DIGEST = '39ba467330f87327eefb5a071b8dec213623c4e3'
    SHA256_DIGEST = 'c55de3986267db6fdf1e4e960e2db01781c67f328da26693b9ff4c7387c6e472'
    CRC32C = '842b10aa'
    S3_ETAG = 'ddd80671f81b6e687bcaff02edea4c3b'

    def check_sums(self, checksums):
        self.assertEqual(checksums['sha1'], self.SHA1_DIGEST)
        self.assertEqual(checksums['sha256'], self.SHA256_DIGEST)
        self.assertEqual(checksums['crc32c'].lower(), self.CRC32C.lower())
        self.assertEqual(checksums['s3_etag'], self.S3_ETAG)

    def test_checksums_after_single_read(self):
        with open(self.FILE_TO_DIGEST, 'rb') as fh:
            reader = ChecksummingBufferedReader(fh)
            reader.read()
            sums = reader.get_checksums()
            self.check_sums(sums)

    def test_checksums_after_multiple_reads(self):
        statinfo = os.stat(self.FILE_TO_DIGEST)
        chunk_size = statinfo.st_size // 4
        with open(self.FILE_TO_DIGEST, 'rb') as raw_fh:
            reader = ChecksummingBufferedReader(raw_fh)
            while True:
                buf = reader.read(chunk_size)
                if not buf:
                    break
            sums = reader.get_checksums()
            self.check_sums(sums)

if __name__ == '__main__':
    unittest.main()
