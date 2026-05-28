import zipfile
import base64
import io

items_out = []

for item in _items:
    json_data = item.get('json', {})
    raw_b64 = item.get('binary', {}).get('data', {}).get('data', '')
    zip_bytes = base64.b64decode(raw_b64)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            # skip directories and macOS metadata
            if name.endswith('/') or name.startswith('__MACOSX') or name.startswith('.'):
                continue

            file_bytes = zf.read(name)
            short_name = name.split('/')[-1]
            ext = short_name.rsplit('.', 1)[-1].lower() if '.' in short_name else ''
            mime_map = {
                'pdf':  'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'txt':  'text/plain',
                'md':   'text/markdown',
            }
            mime_type = mime_map.get(ext, 'application/octet-stream')
            items_out.append({
                'json': {
                    'id': None,
                    'name': short_name,
                    'mimeType': mime_type,
                    'fileExtension': ext,
                    '_fileBase64': base64.b64encode(file_bytes).decode('utf-8'),
                    '_fileName': short_name,
                    '_sourceZip': {
                        'id':   json_data.get('id'),
                        'name': json_data.get('name'),
                    },
                }
            })

return items_out
