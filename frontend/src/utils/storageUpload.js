import apiInstance from './axios';

export const STORAGE_BUCKET = import.meta.env.VITE_STORAGE_BUCKET;

function ensureBucket() {
  if (!STORAGE_BUCKET) {
    throw new Error('Missing VITE_STORAGE_BUCKET');
  }
}

export async function presignUpload({ filename, contentType, keyPrefix }) {
  ensureBucket();
  const { data } = await apiInstance.post('storage/presign-upload/', {
    bucket: STORAGE_BUCKET,
    filename,
    content_type: contentType,
    key_prefix: keyPrefix,
  });
  return data;
}

export async function uploadFileToPresignedUrl({ uploadUrl, file, contentType }) {
  const res = await fetch(uploadUrl, {
    method: 'PUT',
    // Don't force Content-Type. If the signature was generated without Content-Type,
    // sending one here can cause SignatureDoesNotMatch.
    body: file,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Upload failed (${res.status}): ${text}`);
  }
}

export async function uploadFile({ file, keyPrefix }) {
  if (!file) return null;
  const filename = file.name || 'file';
  const contentType = file.type || undefined;

  const presigned = await presignUpload({ filename, contentType, keyPrefix });
  await uploadFileToPresignedUrl({ uploadUrl: presigned.upload_url, file, contentType: presigned.content_type });

  return {
    bucket: presigned.bucket,
    key: presigned.key,
  };
}

export async function presignDownload({ key, expiresIn }) {
  ensureBucket();
  const { data } = await apiInstance.post('storage/presign-download/', {
    bucket: STORAGE_BUCKET,
    key,
    expires_in: expiresIn,
  });
  return data?.url;
}
