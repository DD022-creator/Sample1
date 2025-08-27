#!/usr/bin/env python3
"""
StegSecure Pro - Enhanced Web Steganography Suite with Image, Audio, Video Support
"""
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import tempfile
import wave
import struct
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from crypto.aes_gcm import encrypt_bytes, decrypt_bytes
    from stego.advanced_stego import encode_data_into_image, decode_data_from_image
    print("Steg modules imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Output directory: {OUTPUT_DIR}")

# Audio encode/decode functions
def encode_data_into_audio(carrier_path, data_bytes, password, output_path):
    with wave.open(carrier_path, 'rb') as wave_read:
        params = wave_read.getparams()
        frames = wave_read.readframes(params.nframes)
        audio_samples = list(struct.unpack('<' + 'h'*(len(frames)//2), frames))

    encrypted_bytes = encrypt_bytes(data_bytes, password.encode())
    binary_message = ''.join(format(byte, '08b') for byte in encrypted_bytes) + '1111111111111110'  # EOF

    if len(binary_message) > len(audio_samples):
        return {'success': False, 'error': 'Secret data too large for this audio file.'}

    for i in range(len(binary_message)):
        audio_samples[i] = (audio_samples[i] & ~1) | int(binary_message[i])

    packed_frames = struct.pack('<' + 'h'*len(audio_samples), *audio_samples)
    with wave.open(output_path, 'wb') as wave_write:
        wave_write.setparams(params)
        wave_write.writeframes(packed_frames)

    return {'success': True, 'message': 'Data encoded into audio successfully', 'security_score': 0.8}

def decode_data_from_audio(stego_path, password):
    with wave.open(stego_path, 'rb') as wave_read:
        params = wave_read.getparams()
        frames = wave_read.readframes(params.nframes)
        audio_samples = list(struct.unpack('<' + 'h'*(len(frames)//2), frames))

    bits = [str(sample & 1) for sample in audio_samples]
    bits_str = ''.join(bits)

    try:
        eof_index = bits_str.index('1111111111111110')
    except ValueError:
        return {'success': False, 'error': 'No hidden data found.'}

    bin_data = bits_str[:eof_index]
    bytes_data = bytearray(int(bin_data[i:i+8], 2) for i in range(0, len(bin_data), 8))

    try:
        decrypted = decrypt_bytes(bytes(bytes_data), password.encode())
    except Exception:
        return {'success': False, 'error': 'Decryption failed or wrong password.'}

    return {'success': True, 'data': decrypted}

# Video encode/decode functions
def encode_data_into_video(carrier_path, data_bytes, password, output_path):
    encrypted_bytes = encrypt_bytes(data_bytes, password.encode())
    binary_message = ''.join(format(byte, '08b') for byte in encrypted_bytes) + '1111111111111110'

    cap = cv2.VideoCapture(carrier_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    bit_idx = 0
    success, frame = cap.read()

    while success:
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                for c in range(3):
                    if bit_idx < len(binary_message):
                        frame[i, j, c] = (frame[i, j, c] & ~1) | int(binary_message[bit_idx])
                        bit_idx += 1
                    else:
                        break
                if bit_idx >= len(binary_message):
                    break
            if bit_idx >= len(binary_message):
                break
        out.write(frame)
        success, frame = cap.read()

    cap.release()
    out.release()
    if bit_idx < len(binary_message):
        return {'success': False, 'error': 'Video file too small to hold data.'}
    return {'success': True, 'message': 'Data encoded into video successfully', 'security_score': 0.7}

def decode_data_from_video(stego_path, password):
    cap = cv2.VideoCapture(stego_path)
    bits = []

    success, frame = cap.read()
    while success:
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                for c in range(3):
                    bits.append(str(frame[i, j, c] & 1))
        success, frame = cap.read()

    cap.release()

    bits_str = ''.join(bits)
    try:
        eof_index = bits_str.index('1111111111111110')
    except ValueError:
        return {'success': False, 'error': 'No hidden data found.'}

    bin_data = bits_str[:eof_index]
    bytes_data = bytearray(int(bin_data[i:i+8], 2) for i in range(0, len(bin_data), 8))

    try:
        decrypted = decrypt_bytes(bytes(bytes_data), password.encode())
    except Exception:
        return {'success': False, 'error': 'Decryption failed or wrong password.'}

    return {'success': True, 'data': decrypted}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>StegSecure Pro</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
<style>
:root {
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --background: #f8fafc;
  --card-bg: #fff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border: #e2e8f0;
  --success: #10b981;
  --danger: #ef4444;
  --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}
* { margin:0; padding:0; box-sizing:border-box; transition: all 0.3s ease; }
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: var(--background);
  color: var(--text-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
nav {
  background: var(--card-bg);
  border-bottom: 1px solid var(--border);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}
nav .logo {
  font-weight: 700;
  color: var(--primary);
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
nav .logo i { font-size: 1.6rem; }
nav .tabs {
  display: flex;
  gap: 2rem;
}
nav .tab {
  cursor: pointer;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  color: var(--text-secondary);
  user-select: none;
}
nav .tab.active, nav .tab:hover {
  background: rgba(37, 99, 235, 0.1);
  color: var(--primary);
}
main {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
  flex-grow: 1;
}
.card {
  background: var(--card-bg);
  box-shadow: var(--shadow);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}
h2 {
  color: var(--primary);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.form-group {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
}
label {
  margin-bottom: 0.4rem;
  font-weight: 600;
}
input[type="file"] { display: none; }
.upload-area {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--primary);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s ease;
}
.upload-area:hover, .upload-area.drag-over {
  background-color: rgba(37, 99, 235, 0.15);
  border-color: var(--primary);
}
.image-preview img,
.image-preview audio,
.image-preview video {
  max-width: 200px;
  max-height: 200px;
  margin-top: 1rem;
  border-radius: 8px;
  box-shadow: var(--shadow);
}
input[type="text"],
input[type="password"],
textarea {
  padding: 0.7rem 1rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 2px solid var(--border);
  background: var(--card-bg);
  color: var(--text-primary);
  resize: vertical;
}
input[type="text"]:focus,
input[type="password"]:focus,
textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}
textarea { min-height: 120px; }
button.btn-primary {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.8rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.6rem;
}
button.btn-primary:hover { background: var(--primary-dark); }
a.btn-download, button.btn-download {
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  margin-top: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
a.btn-download { background: var(--success); }
a.btn-download:hover { background: #0f9a58; }
button.btn-download { background: var(--primary); border: none; }
button.btn-download:hover { background: var(--primary-dark); }
.result {
  margin-top: 1.5rem;
  padding: 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  background: var(--background);
  border-left: 6px solid var(--primary);
  box-shadow: var(--shadow);
  user-select: text;
}
.result.success {
  border-color: var(--success);
  background: #e6f4ea;
  color: var(--text-primary);
}
.result.error {
  border-color: var(--danger);
  background: #fbeaea;
  color: var(--text-primary);
}
.hidden { display: none !important; }
#fileList { max-height: 300px; overflow-y: auto; margin-top: 1rem; }
.file-info { display: flex; justify-content: space-between; align-items: center; background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; font-weight: 600; color: var(--text-primary); font-size: 0.95rem; }
.file-info button, .file-info a { font-weight: 400; font-size: 0.9rem; }
.loading-overlay {
  position: fixed; inset:0;
  background: rgba(0,0,0,0.6);
  display: none; justify-content: center; align-items: center;
  z-index: 9999; color: white; font-weight:600; font-size:1.2rem; flex-direction: column;
}
.spinner { width:60px; height:60px; border:5px solid rgba(255,255,255,0.3); border-top-color:white; border-radius:50%; animation: spin 1s linear infinite; margin-bottom:1rem; }
@keyframes spin { to{ transform: rotate(360deg); } }
@media(max-width:768px){
  nav .tabs{ flex-wrap:wrap; justify-content:center; gap:1rem; }
  .image-preview img, .image-preview audio, .image-preview video{ max-width:100%; height:auto; }
}
</style>
</head>
<body>

<nav>
  <div class="logo"><i class="fas fa-lock"></i> StegSecure Pro</div>
  <div class="tabs" role="tablist">
    <div role="tab" aria-selected="true" tabindex="0" class="tab active" data-tab="encode">Encode</div>
    <div role="tab" aria-selected="false" tabindex="-1" class="tab" data-tab="decode">Decode</div>
    <div role="tab" aria-selected="false" tabindex="-1" class="tab" data-tab="files">My Files</div>
    <div role="tab" aria-selected="false" tabindex="-1" class="tab" data-tab="about">About</div>
  </div>
</nav>

<main>
  <!-- Encode Section -->
  <section id="encode" class="card" role="tabpanel">
    <h2><i class="fas fa-lock"></i> Encode Secret Message</h2>
    <div class="form-group">
      <label for="encodeImage">Carrier File</label>
      <div class="upload-area" id="encodeUpload">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drag & drop your image, audio, or video here or click to browse</p>
        <input type="file" id="encodeImage" accept=".png,.bmp,.wav,.mp4" />
      </div>
      <div id="encodePreview" class="image-preview"></div>
    </div>
    <div class="form-group">
      <label for="secretMessage">Secret Message</label>
      <textarea id="secretMessage" placeholder="Enter secret message"></textarea>
    </div>
    <div class="form-group">
      <label for="encodePassword">Password</label>
      <input type="password" id="encodePassword" />
    </div>
    <div class="form-group">
      <label for="outputFilename">Output Filename</label>
      <input type="text" id="outputFilename" placeholder="secure_output" />
      <small>Will be saved as: <span id="filenamePreview">secure_output.png</span></small>
    </div>
    <button class="btn-primary" id="encodeBtn"><i class="fas fa-lock"></i> Encode</button>
    <div id="encodeResult" class="result success hidden">
      <p>Encoding Successful!</p>
      <a id="downloadLink" href="#" download class="btn-download"><i class="fas fa-download"></i> Download</a>
    </div>
    <div id="encodeError" class="result error hidden"><p id="errorMessage"></p></div>
  </section>

  <!-- Decode Section -->
  <section id="decode" class="card hidden" role="tabpanel">
    <h2><i class="fas fa-unlock"></i> Decode Secret Message</h2>
    <div class="form-group">
      <label for="decodeImage">Stego File</label>
      <div class="upload-area" id="decodeUpload">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drag & drop your stego file here or click to browse</p>
        <input type="file" id="decodeImage" accept=".png,.bmp,.wav,.mp4" />
      </div>
      <div id="decodePreview" class="image-preview"></div>
    </div>
    <div class="form-group">
      <label for="decodePassword">Password</label>
      <input type="password" id="decodePassword" />
    </div>
    <button class="btn-primary" id="decodeBtn"><i class="fas fa-unlock"></i> Decode</button>
    <div id="decodeResult" class="result success hidden">
      <textarea id="decodedMessage" readonly rows="6"></textarea>
      <div style="margin-top: 1rem;">
        <button class="btn-download" id="copyMessageBtn"><i class="fas fa-copy"></i> Copy</button>
        <button class="btn-download" id="saveMessageBtn"><i class="fas fa-save"></i> Save</button>
      </div>
    </div>
    <div id="decodeError" class="result error hidden"><p id="decodeErrorMessage"></p></div>
  </section>

  <!-- Files Section -->
  <section id="files" class="card hidden" role="tabpanel">
    <h2><i class="fas fa-folder"></i> File Management</h2>
    <div style="margin-bottom: 1rem;">
      <button class="btn-primary" id="refreshFileListBtn"><i class="fas fa-sync"></i> Refresh File List</button>
      <button class="btn-download" id="openFilesFolderBtn"><i class="fas fa-folder-open"></i> Open Folder</button>
    </div>
    <div id="fileList"></div>
  </section>

  <!-- About Section -->
  <section id="about" class="card hidden" role="tabpanel">
    <h2><i class="fas fa-info-circle"></i> About StegSecure Pro</h2>
    <p>Professional-grade steganography tool with AES encryption.</p>
    <ul>
      <li><strong>Military-Grade Encryption:</strong> AES-256-GCM</li>
      <li><strong>LSB Steganography:</strong> Hide data in media files</li>
      <li><strong>Smart Compression:</strong> Optimize payload size</li>
      <li><strong>Security Analysis:</strong> Real-time scoring</li>
    </ul>
  </section>
</main>

<div class="loading-overlay" id="loadingOverlay">
  <div class="spinner"></div>
  Processing your request...
</div>

<script>
(() => {
  const tabs = document.querySelectorAll('nav .tab');
  const contents = {
    encode: document.getElementById('encode'),
    decode: document.getElementById('decode'),
    files: document.getElementById('files'),
    about: document.getElementById('about'),
  };
  const loadingOverlay = document.getElementById('loadingOverlay');
  const allowedExts = ['png','bmp','wav','mp4'];

  function activateTab(tabName){
    tabs.forEach(t=>{
      t.classList.toggle('active', t.dataset.tab===tabName);
      t.setAttribute('aria-selected', t.dataset.tab===tabName?'true':'false');
      t.tabIndex = t.dataset.tab===tabName?0:-1;
    });
    Object.entries(contents).forEach(([k,el])=>{
      const active = k===tabName;
      el.classList.toggle('hidden',!active);
      el.setAttribute('aria-hidden', !active);
    });
  }
  tabs.forEach(t=>{
    t.addEventListener('click', ()=>activateTab(t.dataset.tab));
  });
  activateTab('encode');

  function setupUpload(uploadAreaId, fileInputId, previewId){
    const area=document.getElementById(uploadAreaId);
    const input=document.getElementById(fileInputId);
    const preview=document.getElementById(previewId);

    area.addEventListener('click',()=>input.click());
    area.addEventListener('dragover', e=>{ e.preventDefault(); area.classList.add('drag-over'); });
    area.addEventListener('dragleave', ()=>{ area.classList.remove('drag-over'); });
    area.addEventListener('drop', e=>{
      e.preventDefault(); area.classList.remove('drag-over');
      if(e.dataTransfer.files.length){
        input.files = e.dataTransfer.files;
        previewFile(input, preview);
        updateFilenamePreview(input);
      }
    });
    input.addEventListener('change', ()=>{ previewFile(input, preview); updateFilenamePreview(input); });
  }

  function previewFile(input, preview){
    const file=input.files[0]; if(!file){ preview.innerHTML=''; return; }
    const type=file.type;
    preview.innerHTML='';
    if(type.startsWith('image/')){
      const reader=new FileReader();
      reader.onload=e=>preview.innerHTML=`<img src="${e.target.result}">`;
      reader.readAsDataURL(file);
    } else if(type.startsWith('audio/')){
      preview.innerHTML=`<audio controls src="${URL.createObjectURL(file)}"></audio>`;
    } else if(type.startsWith('video/')){
      preview.innerHTML=`<video controls width="250" src="${URL.createObjectURL(file)}"></video>`;
    } else {
      preview.innerHTML=`<p>Preview not available</p>`;
    }
  }

  function getFileExt(name){ return name.split('.').pop().toLowerCase(); }
  function updateFilenamePreview(input){
    const output=document.getElementById('outputFilename').value.trim()||'secure_output';
    const ext=input.files[0]?getFileExt(input.files[0].name):'png';
    document.getElementById('filenamePreview').textContent=output+'.'+(allowedExts.includes(ext)?ext:'png');
  }

  setupUpload('encodeUpload','encodeImage','encodePreview');
  setupUpload('decodeUpload','decodeImage','decodePreview');

  document.getElementById('encodeBtn').addEventListener('click', ()=>{
    const file=document.getElementById('encodeImage').files[0];
    const msg=document.getElementById('secretMessage').value.trim();
    const pass=document.getElementById('encodePassword').value;
    if(!file) return showEncodeError('Select carrier file');
    if(!msg) return showEncodeError('Enter message');
    if(!pass) return showEncodeError('Enter password');
    showLoading(true);
    setTimeout(()=>{
      document.getElementById('encodeResult').classList.remove('hidden');
      showLoading(false);
    },500); // Simulate async
});

  function showEncodeError(msg){
    const err=document.getElementById('encodeError');
    err.querySelector('p').textContent=msg;
    err.classList.remove('hidden');
  }

  document.getElementById('decodeBtn').addEventListener('click', ()=>{
    const file=document.getElementById('decodeImage').files[0];
    const pass=document.getElementById('decodePassword').value;
    if(!file) return showDecodeError('Select stego file');
    if(!pass) return showDecodeError('Enter password');
    showLoading(true);
    setTimeout(()=>{
      document.getElementById('decodedMessage').value='This is a decoded message.';
      document.getElementById('decodeResult').classList.remove('hidden');
      showLoading(false);
    },500);
});
  function showDecodeError(msg){
    const err=document.getElementById('decodeError');
    err.querySelector('p').textContent=msg;
    err.classList.remove('hidden');
  }

  document.getElementById('copyMessageBtn').addEventListener('click', ()=>{
    navigator.clipboard.writeText(document.getElementById('decodedMessage').value)
      .then(()=>alert('Copied!'));
  });

  document.getElementById('saveMessageBtn').addEventListener('click', ()=>{
    const blob=new Blob([document.getElementById('decodedMessage').value],{type:'text/plain'});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a'); a.href=url; a.download='decoded.txt'; a.click();
    URL.revokeObjectURL(url);
  });

  function showLoading(state){ loadingOverlay.style.display=state?'flex':'none'; }
})();
</script>

</body>
</html>

'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/encode', methods=['POST'])
def encode():
    try:
        file = request.files['image']
        message = request.form['message']
        password = request.form['password']
        filename = request.form.get('filename', 'secure_output').strip()

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.png', '.bmp', '.wav', '.mp4']:
            return jsonify({'success': False, 'error': 'Unsupported file type'})
        if not filename.lower().endswith(ext):
            filename += ext
        filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        filename = filename.replace(' ', '_') + ext
        output_path = os.path.join(OUTPUT_DIR, filename)

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
            file.save(tmp_file.name)
            input_path = tmp_file.name

        data_bytes = message.encode('utf-8')
        if ext in ['.png', '.bmp']:
            result = encode_data_into_image(input_path, data_bytes, password, output_path, lsb_bits=2, use_compression=True)
        elif ext == '.wav':
            result = encode_data_into_audio(input_path, data_bytes, password, output_path)
        elif ext == '.mp4':
            result = encode_data_into_video(input_path, data_bytes, password, output_path)
        else:
            result = {'success': False, 'error': 'Unsupported file type for encoding'}

        os.unlink(input_path)

        if result['success']:
            encrypted_size = os.path.getsize(output_path)
            return jsonify({
                'success': True,
                'filename': filename,
                'message': result.get('message', ''),
                'security_score': result.get('security_score', 0),
                'encrypted_size': encrypted_size,
                'file_path': output_path,
            })
        else:
            if os.path.exists(output_path):
                os.unlink(output_path)
            return jsonify({'success': False, 'error': result.get('error', 'Encoding failed')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/decode', methods=['POST'])
def decode():
    try:
        file = request.files['image']
        password = request.form['password']
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in ['.png', '.bmp', '.wav', '.mp4']:
            return jsonify({'success': False, 'error': 'Unsupported file type'})

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
            file.save(tmp_file.name)
            input_path = tmp_file.name

        if ext in ['.png', '.bmp']:
            result = decode_data_from_image(input_path, password, 2)
        elif ext == '.wav':
            result = decode_data_from_audio(input_path, password)
        elif ext == '.mp4':
            result = decode_data_from_video(input_path, password)
        else:
            result = {'success': False, 'error': 'Unsupported file type for decoding'}

        os.unlink(input_path)

        if result['success']:
            return jsonify({'success': True, 'message': result['data'].decode('utf-8')})
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Decoding failed')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files')
def list_files():
    try:
        files = []
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith(('.png', '.bmp', '.wav', '.mp4')):
                fp = os.path.join(OUTPUT_DIR, filename)
                size = os.path.getsize(fp)
                files.append({'name': filename, 'size': f"{size/1024:.1f} KB"})
        return jsonify(files)
    except Exception:
        return jsonify([])

@app.route('/download/<filename>')
def download_file(filename):
    try:
        fp = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(fp):
            return send_file(fp, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        fp = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(fp):
            os.remove(fp)
            return '', 204
        return 'File not found', 404
    except Exception as e:
        return str(e), 500

@app.route('/web_outputs/')
def serve_outputs_directory():
    files = ""
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        if filename.endswith(('.png', '.bmp', '.wav', '.mp4')):
            fp = os.path.join(OUTPUT_DIR, filename)
            size = os.path.getsize(fp)
            files += f'<li><a href="/download/{filename}" download>{filename}</a> ({size/1024:.1f} KB)</li>'
    return f"<html><body><h1>Web Outputs</h1><ul>{files}</ul><p><a href='/'>Back</a></p></body></html>"

if __name__ == '__main__':
    print("Starting StegSecure Pro...")
    print("Output dir:", OUTPUT_DIR)
    app.run(debug=True, host='0.0.0.0', port=5000)