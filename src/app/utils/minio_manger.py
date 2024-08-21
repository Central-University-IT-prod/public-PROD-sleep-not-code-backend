from typing import Self

from minio import Minio


class MinioManger:
    def __init__(
        self: Self, endpoint: str, access_key: str, secret_key: str, bucket_name: str
    ) -> None:
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.client = Minio(self.endpoint, self.access_key, self.secret_key)

    def create_bucket(self: Self) -> None:
        found = self.client.bucket_exists(self.bucket_name)
        if not found:
            self.client.make_bucket(self.bucket_name)

    def upload_file(self: Self, filename: str, source_file: str) -> None:
        self.client.fput_object(
            self.bucket_name,
            filename,
            source_file,
        )

    def download_file(self: Self, filename: str, path: str) -> None:
        self.client.fget_object(self.bucket_name, filename, path)
