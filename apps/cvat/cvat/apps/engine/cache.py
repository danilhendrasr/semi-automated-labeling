# Copyright (C) 2020-2021 Intel Corporation
#
# SPDX-License-Identifier: MIT

import os
from io import BytesIO

from diskcache import Cache
from django.conf import settings
from tempfile import NamedTemporaryFile

from cvat.apps.engine.log import slogger
from cvat.apps.engine.media_extractors import (Mpeg4ChunkWriter,
    Mpeg4CompressedChunkWriter, ZipChunkWriter, ZipCompressedChunkWriter,
    ImageDatasetManifestReader, VideoDatasetManifestReader)
from cvat.apps.engine.models import DataChoice, StorageChoice
from cvat.apps.engine.models import DimensionType
from cvat.apps.engine.cloud_provider import get_cloud_storage_instance, Credentials, Status
from cvat.apps.engine.utils import md5_hash
class CacheInteraction:
    def __init__(self, dimension=DimensionType.DIM_2D):
        self._cache = Cache(settings.CACHE_ROOT)
        self._dimension = dimension

    def __del__(self):
        self._cache.close()

    def get_buff_mime(self, chunk_number, quality, db_data):
        chunk, tag = self._cache.get('{}_{}_{}'.format(db_data.id, chunk_number, quality), tag=True)

        if not chunk:
            chunk, tag = self.prepare_chunk_buff(db_data, quality, chunk_number)
            self.save_chunk(db_data.id, chunk_number, quality, chunk, tag)
        return chunk, tag

    def prepare_chunk_buff(self, db_data, quality, chunk_number):
        from cvat.apps.engine.frame_provider import FrameProvider # TODO: remove circular dependency
        writer_classes = {
            FrameProvider.Quality.COMPRESSED : Mpeg4CompressedChunkWriter if db_data.compressed_chunk_type == DataChoice.VIDEO else ZipCompressedChunkWriter,
            FrameProvider.Quality.ORIGINAL : Mpeg4ChunkWriter if db_data.original_chunk_type == DataChoice.VIDEO else ZipChunkWriter,
        }

        image_quality = 100 if writer_classes[quality] in [Mpeg4ChunkWriter, ZipChunkWriter] else db_data.image_quality
        mime_type = 'video/mp4' if writer_classes[quality] in [Mpeg4ChunkWriter, Mpeg4CompressedChunkWriter] else 'application/zip'

        kwargs = {}
        if self._dimension == DimensionType.DIM_3D:
            kwargs["dimension"] = DimensionType.DIM_3D
        writer = writer_classes[quality](image_quality, **kwargs)

        images = []
        buff = BytesIO()
        upload_dir = {
                StorageChoice.LOCAL: db_data.get_upload_dirname(),
                StorageChoice.SHARE: settings.SHARE_ROOT,
                StorageChoice.CLOUD_STORAGE: db_data.get_upload_dirname(),
            }[db_data.storage]
        if hasattr(db_data, 'video'):
            source_path = os.path.join(upload_dir, db_data.video.path)

            reader = VideoDatasetManifestReader(manifest_path=db_data.get_manifest_path(),
                source_path=source_path, chunk_number=chunk_number,
                chunk_size=db_data.chunk_size, start=db_data.start_frame,
                stop=db_data.stop_frame, step=db_data.get_frame_step())
            for frame in reader:
                images.append((frame, source_path, None))
        else:
            reader = ImageDatasetManifestReader(manifest_path=db_data.get_manifest_path(),
                chunk_number=chunk_number, chunk_size=db_data.chunk_size,
                start=db_data.start_frame, stop=db_data.stop_frame,
                step=db_data.get_frame_step())
            if db_data.storage == StorageChoice.CLOUD_STORAGE:
                db_cloud_storage = db_data.cloud_storage
                assert db_cloud_storage, 'Cloud storage instance was deleted'
                credentials = Credentials()
                credentials.convert_from_db({
                    'type': db_cloud_storage.credentials_type,
                    'value': db_cloud_storage.credentials,
                })
                details = {
                    'resource': db_cloud_storage.resource,
                    'credentials': credentials,
                    'specific_attributes': db_cloud_storage.get_specific_attributes()
                }
                try:
                    cloud_storage_instance = get_cloud_storage_instance(cloud_provider=db_cloud_storage.provider_type, **details)
                    for item in reader:
                        file_name = f"{item['name']}{item['extension']}"
                        with NamedTemporaryFile(mode='w+b', prefix='cvat', suffix=file_name.replace(os.path.sep, '#'), delete=False) as temp_file:
                            source_path = temp_file.name
                            buf = cloud_storage_instance.download_fileobj(file_name)
                            temp_file.write(buf.getvalue())
                            temp_file.flush()
                            checksum = item.get('checksum', None)
                            if not checksum:
                                slogger.cloud_storage[db_cloud_storage.id].warning('A manifest file does not contain checksum for image {}'.format(item.get('name')))
                            if checksum and not md5_hash(source_path) == checksum:
                                slogger.cloud_storage[db_cloud_storage.id].warning('Hash sums of files {} do not match'.format(file_name))
                            images.append((source_path, source_path, None))
                except Exception as ex:
                    storage_status = cloud_storage_instance.get_status()
                    if storage_status == Status.FORBIDDEN:
                        msg = 'The resource {} is no longer available. Access forbidden.'.format(cloud_storage_instance.name)
                    elif storage_status == Status.NOT_FOUND:
                        msg = 'The resource {} not found. It may have been deleted.'.format(cloud_storage_instance.name)
                    else:
                        # check status of last file
                        file_status = cloud_storage_instance.get_file_status(file_name)
                        if file_status == Status.NOT_FOUND:
                            raise Exception("'{}' not found on the cloud storage '{}'".format(file_name, cloud_storage_instance.name))
                        elif file_status == Status.FORBIDDEN:
                            raise Exception("Access to the file '{}' on the '{}' cloud storage is denied".format(file_name, cloud_storage_instance.name))
                        msg = str(ex)
                    raise Exception(msg)
            else:
                for item in reader:
                    source_path = os.path.join(upload_dir, f"{item['name']}{item['extension']}")
                    images.append((source_path, source_path, None))
        writer.save_as_chunk(images, buff)
        buff.seek(0)
        if db_data.storage == StorageChoice.CLOUD_STORAGE:
            images = [image[0] for image in images if os.path.exists(image[0])]
            for image_path in images:
                os.remove(image_path)
        return buff, mime_type

    def save_chunk(self, db_data_id, chunk_number, quality, buff, mime_type):
        self._cache.set('{}_{}_{}'.format(db_data_id, chunk_number, quality), buff, tag=mime_type)
