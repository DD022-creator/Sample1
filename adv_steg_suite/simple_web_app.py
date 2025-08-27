import os
import time
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS

# ✅ Import your stego modules
from stego.advanced_stego import (
    encode_data_into_image,
    decode_data_from_image
)
from stego.audio_stego import (
    embed_lsb_audio,
    extract_lsb_audio
)
from stego.video_stego import (
    embed_lsb_video,
    extract_lsb_video
)

app = Flask(__name__)
CORS(app)

# Output folder
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "web_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------ In-memory library ------------------
file_library = []

def add_to_library(file_path, file_type, operation, message=None):
    file_library.append({
        "file_path": "/web_outputs/" + os.path.basename(file_path),
        "file_type": file_type,
        "operation": operation,  # "encode" or "decode"
        "message": message
    })

# ------------------ HTML Template ------------------
HTML_TEMPLATE = """ 
<html>
<head>
  <title>Steganography Suite</title>
  <style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; margin: 0; padding: 0; color: #333; }
    header { background: linear-gradient(135deg, #4e73df, #1cc88a); color: white; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
    h1 { font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 20px; background: linear-gradient(90deg, #007bff, #6f42c1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 2px 2px 8px rgba(0,0,0,0.25); letter-spacing: 2px; }
    main { max-width: 900px; margin: 30px auto; padding: 20px; }
    .tab { background: white; border-radius: 12px; padding: 20px; margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.05); transition: transform 0.2s ease-in-out; }
    .tab:hover { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); }
    h2 { margin-top: 0; font-size: 1.4rem; color: #4e73df; }
    input[type="file"], textarea, button { width: 100%; padding: 10px; margin: 10px 0; border-radius: 8px; border: 1px solid #ccc; font-size: 1rem; box-sizing: border-box; }
    textarea, input[type="text"], input[type="password"] { height: 80px; resize: vertical; }
    button { background: linear-gradient(135deg, #6a11cb, #2575fc); color: white; border: none; padding: 12px 22px; border-radius: 50px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.3s ease-in-out; box-shadow: 0 4px 10px rgba(0,0,0,0.2); margin: 8px 5px; }
    button:hover { background: linear-gradient(135deg, #2575fc, #6a11cb); transform: translateY(-3px) scale(1.05); box-shadow: 0 8px 18px rgba(0,0,0,0.25); }
    button:active { transform: translateY(0) scale(0.97); box-shadow: 0 3px 8px rgba(0,0,0,0.2); }
    input[type="file"] { display: none; }
    .custom-file-upload { background: linear-gradient(135deg, #ff7eb3, #ff758c); color: white; padding: 12px 22px; border-radius: 50px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.3s ease-in-out; box-shadow: 0 4px 10px rgba(0,0,0,0.2); display: inline-block; margin: 8px 5px; }
    .custom-file-upload:hover { background: linear-gradient(135deg, #ff758c, #ff7eb3); transform: translateY(-3px) scale(1.05); box-shadow: 0 8px 18px rgba(0,0,0,0.25); }
    .custom-file-upload:active { transform: translateY(0) scale(0.97); box-shadow: 0 3px 8px rgba(0,0,0,0.2); }
    .files { margin-top: 10px; }
    .files a { display: block; margin: 6px 0; color: #4e73df; text-decoration: none; }
    .files a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>🔐 Advanced Steganography Suite</h1>
  <main>
    <!-- Image Encode -->
    <div class="tab">
      <h2>Image Encode</h2>
      <form id="imgEncodeForm" enctype="multipart/form-data">
        <input type="file" name="cover" required />
        <p class="custom-file-upload">📷 Click or drag & drop image</p>
        <input type="text" name="message" placeholder="Secret text" />
        <button type="submit">Encode</button>
      </form>
    </div>

    <!-- Image Decode -->
    <div class="tab">
      <h2>Image Decode</h2>
      <form id="imgDecodeForm" enctype="multipart/form-data">
        <input type="file" name="stego" required />
        <button type="submit">Decode</button>
        <textarea id="imgDecodeOutput" placeholder="Decoded message will appear here..." readonly></textarea>
      </form>
    </div>

    <!-- Audio Encode -->
    <div class="tab">
      <h2>Audio Encode</h2>
      <form id="audEncodeForm" enctype="multipart/form-data">
        <input type="file" name="cover" accept=".wav" required />
        <p class="custom-file-upload">🎵 Click or drag & drop audio</p>
        <input type="text" name="message" placeholder="Secret text" />
        <button type="submit">Encode</button>
      </form>
    </div>

    <!-- Audio Decode -->
    <div class="tab">
      <h2>Audio Decode</h2>
      <form id="audDecodeForm" enctype="multipart/form-data">
        <input type="file" name="stego" accept=".wav" required />
        <button type="submit">Decode</button>
        <textarea id="audDecodeOutput" placeholder="Decoded message will appear here..." readonly></textarea>
      </form>
    </div>

    <!-- Video Encode -->
    <div class="tab">
      <h2>Video Encode</h2>
      <form id="vidEncodeForm" enctype="multipart/form-data">
        <input type="file" name="cover" accept=".mp4" required />
        <p class="custom-file-upload">🎬 Click or drag & drop video</p>
        <input type="text" name="message" placeholder="Secret text" />
        <button type="submit">Encode</button>
      </form>
    </div>

    <!-- Video Decode -->
    <div class="tab">
      <h2>Video Decode</h2>
      <form id="vidDecodeForm" enctype="multipart/form-data">
        <input type="file" name="stego" accept=".mp4" required />
        <button type="submit">Decode</button>
         <textarea id="vidDecodeOutput" placeholder="Decoded message will appear here..." readonly></textarea>
      </form>
    </div>

    <!-- Files Section -->
    <div id="file-links">
      <h2>Encoded/Decoded Files</h2>
    </div>
  </main>

  <script>
document.addEventListener("DOMContentLoaded", () => {

  function capitalize(word) {
    return word.charAt(0).toUpperCase() + word.slice(1);
  }

  // File upload click + drag & drop
  document.querySelectorAll('.custom-file-upload').forEach(label => {
    const input = label.previousElementSibling;
    const form = label.closest('form');
    let previewDiv = form.querySelector('.preview');
    if(!previewDiv) {
      previewDiv = document.createElement('div'); previewDiv.className='preview';
      form.insertBefore(previewDiv, label.nextSibling);
    }

    label.addEventListener('click', ()=>input.click());
    label.addEventListener('dragover', e=>{e.preventDefault(); label.style.background='#ffb6c1';});
    label.addEventListener('dragleave', e=>{ label.style.background=''; });
    label.addEventListener('drop', e=>{
      e.preventDefault(); label.style.background='';
      if(e.dataTransfer.files.length){ input.files = e.dataTransfer.files; handlePreview(input, previewDiv); }
    });
    input.addEventListener('change', ()=>handlePreview(input, previewDiv));
  });

  function handlePreview(input, previewDiv){
    const file = input.files[0]; if(!file) return;
    const reader = new FileReader();
    reader.onload = (e)=>{
      previewDiv.innerHTML="";
      if(file.type.startsWith("image/")) previewDiv.innerHTML=`<img src="${e.target.result}" style="max-width:150px;">`;
      else if(file.type.startsWith("audio/")) previewDiv.innerHTML=`<audio controls src="${e.target.result}"></audio>`;
      else if(file.type.startsWith("video/")) previewDiv.innerHTML=`<video controls width="200" src="${e.target.result}"></video>`;
    };
    reader.readAsDataURL(file);
  }

  // Form submit
  async function handleForm(formId, endpoint, isDecode=false){
    const form = document.getElementById(formId);
    form.addEventListener("submit", async e=>{
      e.preventDefault();
      const formData = new FormData(form);
      try{
        const res = await fetch(endpoint, { method:"POST", body:formData });
        const data = await res.json();
        if(data.error){ alert("❌ "+data.error);}
        updateLibrary();
      }catch(err){ console.error(err); alert("⚠️ Something went wrong. Check console."); }
    });
  }

  // Update the library section
  async function updateLibrary() {
    const res = await fetch("/api/library");
    const files = await res.json();
    const libDiv = document.getElementById("file-links");
    libDiv.innerHTML = "<h2>Encoded/Decoded Files</h2>";
    files.forEach(f=>{
      const div = document.createElement("div");
      if(f.file_type==="image") div.innerHTML=`<img src="${f.file_path}" style="max-width:150px;">`;
      else if(f.file_type==="audio") div.innerHTML=`<audio controls src="${f.file_path}"></audio>`;
      else if(f.file_type==="video") div.innerHTML=`<video controls width="200" src="${f.file_path}"></video>`;
      
      if(f.operation==="decode" && f.message) {
        const msg=document.createElement("div");
        msg.innerHTML=`<strong>Decoded Message:</strong> ${f.message}`;
        div.appendChild(msg);
      }
      libDiv.appendChild(div);
    });
  }

  handleForm("imgEncodeForm","/api/encode_image");
  handleForm("imgDecodeForm","/api/decode_image",true);
  handleForm("audEncodeForm","/api/encode_audio");
  handleForm("audDecodeForm","/api/decode_audio",true);
  handleForm("vidEncodeForm","/api/encode_video");
  handleForm("vidDecodeForm","/api/decode_video",true);

  updateLibrary(); // Load library on page load

});
  </script>
</body>
</html>
"""

# ------------------ Flask Routes ------------------
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

# Image Encode
@app.route("/api/encode_image", methods=["POST"])
def encode_image():
    cover = request.files["cover"]
    message = request.form.get("message","")
    cover_path = os.path.join(OUTPUT_DIR, "cover.png")
    stego_path = os.path.join(OUTPUT_DIR, "output.png")
    cover.save(cover_path)
    encode_data_into_image(cover_path, message.encode("utf-8"), stego_path)
    return jsonify({"message":"Image encoded","stego_file":"/web_outputs/output.png"})

# Image Decode
@app.route("/api/decode_image", methods=["POST"])
def decode_image():
    stego_path = os.path.join(OUTPUT_DIR, "output.png")
    data = decode_data_from_image(stego_path)
    return jsonify({"message":"Image decoded","data":data.decode("utf-8")})

# Audio Encode
@app.route("/api/encode_audio", methods=["POST"])
def encode_audio():
    cover = request.files["cover"]
    message = request.form.get("message","")
    cover_path = os.path.join(OUTPUT_DIR, "cover.wav")
    stego_path = os.path.join(OUTPUT_DIR, "output.wav")
    cover.save(cover_path)
    embed_lsb_audio(cover_path, message.encode("utf-8"), stego_path)
    return jsonify({"message":"Audio encoded","stego_file":"/web_outputs/output.wav"})

# Audio Decode
@app.route("/api/decode_audio", methods=["POST"])
def decode_audio():
    stego_path = os.path.join(OUTPUT_DIR, "output.wav")
    data = extract_lsb_audio(stego_path)
    return jsonify({"message":"Audio decoded","data":data.decode("utf-8")})

# Video Encode
@app.route("/api/encode_video", methods=["POST"])
def encode_video():
    cover = request.files["cover"]
    message = request.form.get("message","")
    cover_path = os.path.join(OUTPUT_DIR, "cover.mp4")
    stego_path = os.path.join(OUTPUT_DIR, "output.mp4")
    cover.save(cover_path)
    embed_lsb_video(cover_path, message.encode("utf-8"), stego_path)
    return jsonify({"message":"Video encoded","stego_file":"/web_outputs/output.mp4"})

# Video Decode
@app.route("/api/decode_video", methods=["POST"])
def decode_video():
    stego_path = os.path.join(OUTPUT_DIR, "output.mp4")
    data = extract_lsb_video(stego_path)
    return jsonify({"message":"Video decoded","data":data.decode("utf-8")})

# ---------- Library route ----------
@app.route("/api/library")
def get_library():
    return jsonify(file_library)

# ---------- Serve web_outputs ----------
@app.route("/web_outputs/<path:filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# ------------------ Run Flask ------------------
if __name__ == "__main__":
    app.run(debug=True)
