import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings as s


class StorageService:
    def __init__(self):
        env = s.ENVIRONMENT

        if env == "local":
            self._endpoint_url = s.MINIO_ENDPOINT_URL
        else:
            self._endpoint_url = None

        self._aws_access_key_id = s.AWS_ACCESS_KEY_ID
        self._aws_secret_access_key = s.AWS_SECRET_ACCESS_KEY
        self._region = s.AWS_REGION
        self._bucket_name = s.S3_BUCKET_NAME

        self.s3_client = boto3.client(
            "s3",
            region_name=self._region,
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
        )

    def upload_file(self, file_name: str, data: bytes, content_type: str | None = None):
        try:
            self.s3_client.put_object(
                Bucket=self._bucket_name,
                Key=file_name,
                Body=data,
                # ContentType=content_type,
            )
        except (BotoCoreError, ClientError) as e:
            raise Exception(f"Failed to upload file: {e}")

    def upload_file_from_path(
        self, local_path: str, destination_path: str, content_type: str | None = None
    ):
        try:
            with open(local_path, "rb") as f:
                data = f.read()
            self.upload_file(
                file_name=destination_path, data=data, content_type=content_type
            )
        except OSError as e:
            raise Exception(f"Failed to read local file: {e}")

    def generate_presigned_url(self, *, file_name: str, expires_in=604800) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket_name, "Key": file_name},
            ExpiresIn=expires_in,
        )

    def get_file(self, *, file_name: str, save_dir: str):
        os.makedirs(save_dir, exist_ok=True)
        local_path = os.path.join(save_dir, os.path.basename(file_name))

        with open(local_path, "wb") as f:
            try:
                self.s3_client.download_fileobj(self._bucket_name, file_name, f)
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    raise
                else:
                    raise

    def check_head_object(self, *, file_name: str):
        try:
            self.s3_client.head_object(Bucket=self._bucket_name, Key=file_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise
            else:
                raise


storage_service = StorageService()
