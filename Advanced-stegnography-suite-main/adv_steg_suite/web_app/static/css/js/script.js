// Tab navigation handler
function openTab(evt, tabName) {
  const tabcontent = document.getElementsByClassName("tabcontent");
  for (let i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  const tablinks = document.getElementsByClassName("tablinks");
  for (let i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

// Helper to capitalize first letter
function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

// File preview function for image/audio/video
function handleFileSelect(fileInput, preview, type) {
  const file = fileInput.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    preview.innerHTML = "";
    if (type === "image") {
      const img = document.createElement("img");
      img.src = e.target.result;
      img.style.maxWidth = "150px";
      preview.appendChild(img);
    } else if (type === "audio") {
      const audio = document.createElement("audio");
      audio.src = e.target.result;
      audio.controls = true;
      preview.appendChild(audio);
    } else if (type === "video") {
      const video = document.createElement("video");
      video.src = e.target.result;
      video.controls = true;
      video.style.maxWidth = "200px";
      preview.appendChild(video);
    }
  };
  reader.readAsDataURL(file);
}

// Setup drag & drop and click for file uploads
function setupFileUpload(uploadAreaId, fileInputId, previewId, type) {
  const uploadArea = document.getElementById(uploadAreaId);
  const fileInput = document.getElementById(fileInputId);
  const preview = document.getElementById(previewId);
  if (!uploadArea || !fileInput || !preview) return;

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, e => {
      e.preventDefault();
      e.stopPropagation();
    }, false);
  });

  ['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, () => uploadArea.classList.add('drag-over'));
  });

  ['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('drag-over'));
  });

  uploadArea.addEventListener('click', () => fileInput.click());

  uploadArea.addEventListener('drop', e => {
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      handleFileSelect(fileInput, preview, type);
    }
  });

  fileInput.addEventListener('change', () => {
    handleFileSelect(fileInput, preview, type);
  });
}

// Handle encoding, download encoded file & update library
async function encodeFile(mode, fileInputId, msgInputId) {
  const fileInput = document.getElementById(fileInputId);
  const msgInput = document.getElementById(msgInputId);
  if (!fileInput.files.length || !msgInput.value.trim()) {
    alert("Please select a file and enter a secret message.");
    return;
  }
  const formData = new FormData();
  formData.append("cover", fileInput.files[0]);
  formData.append("message", msgInput.value.trim());

  try {
    const response = await fetch(`/api/encode_${mode}`, { method: "POST", body: formData });
    const data = await response.json();
    if (!response.ok || data.error) {
      alert("Encode failed: " + (data.error || response.statusText));
      return;
    }
    if (data.stego_file) {
      const a = document.createElement("a");
      a.href = data.stego_file;
      a.download = `encoded_${mode}.${mode === "image" ? "png" : mode === "audio" ? "wav" : "mp4"}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    }
    updateLibrary();
  } catch (e) {
    alert("Encode error: " + e.message);
  }
}

// Handle decoding, download decoded file if any & update library
async function decodeFile(mode, fileInputId, outputId) {
  const fileInput = document.getElementById(fileInputId);
  const output = document.getElementById(outputId);
  if (!fileInput.files.length) {
    alert("Please select a stego file to decode.");
    return;
  }
  const formData = new FormData();
  formData.append("stego", fileInput.files[0]);

  try {
    const response = await fetch(`/api/decode_${mode}`, { method: "POST", body: formData });
    const data = await response.json();
    if (!response.ok || data.error) {
      alert("Decode failed: " + (data.error || response.statusText));
      return;
    }
    if (data.decoded_file) {
      const a = document.createElement("a");
      a.href = data.decoded_file;
      a.download = `decoded_${mode}_${Date.now()}.txt`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    }
    if (output) {
      output.value = data.data || "";
    } else if (data.data) {
      alert("Decoded message: " + data.data);
    }
    updateLibrary();
  } catch (e) {
    alert("Decode error: " + e.message);
  }
}

// Update library UI with media previews and text messages
async function updateLibrary() {
  const libDiv = document.getElementById("file-links");
  if (!libDiv) return;
  try {
    const res = await fetch("/api/library");
    const files = await res.json();
    libDiv.innerHTML = "<h2>Encoded/Decoded Files</h2>";
    files.forEach(f => {
      const div = document.createElement("div");
      if (f.file_type === "image") {
        div.innerHTML = `<img src="${f.file_path}" style="max-width:150px;">`;
      } else if (f.file_type === "audio") {
        div.innerHTML = `<audio controls src="${f.file_path}"></audio>`;
      } else if (f.file_type === "video") {
        div.innerHTML = `<video controls width="200" src="${f.file_path}"></video>`;
      }
      if (f.operation === "decode" && f.message) {
        const msg = document.createElement("div");
        msg.innerHTML = `<strong>Decoded Message:</strong> ${f.message}`;
        div.appendChild(msg);
      }
      libDiv.appendChild(div);
    });
  } catch (e) {
    console.error("Library update failed:", e);
  }
}

// DOM Ready - Setup uploads and event listeners
window.onload = () => {
  // Setup tabs - open first tab by default
  const firstTabButton = document.querySelector(".tablinks");
  if (firstTabButton) firstTabButton.click();

  setupFileUpload("imgEncodeUpload", "encodeImageFile", "imgEncodePreview", "image");
  setupFileUpload("imgDecodeUpload", "decodeImageFile", "imgDecodePreview", "image");

  setupFileUpload("audEncodeUpload", "encodeAudioFile", "audEncodePreview", "audio");
  setupFileUpload("audDecodeUpload", "decodeAudioFile", "audDecodePreview", "audio");

  setupFileUpload("vidEncodeUpload", "encodeVideoFile", "vidEncodePreview", "video");
  setupFileUpload("vidDecodeUpload", "decodeVideoFile", "vidDecodePreview", "video");

  document.getElementById("imgEncodeBtn").addEventListener("click", () => encodeFile("image", "encodeImageFile", "encodeImageMsg"));
  document.getElementById("imgDecodeBtn").addEventListener("click", () => decodeFile("image", "decodeImageFile", "decodeImageOutput"));

  document.getElementById("audEncodeBtn").addEventListener("click", () => encodeFile("audio", "encodeAudioFile", "encodeAudioMsg"));
  document.getElementById("audDecodeBtn").addEventListener("click", () => decodeFile("audio", "decodeAudioFile", "decodeAudioOutput"));

  document.getElementById("vidEncodeBtn").addEventListener("click", () => encodeFile("video", "encodeVideoFile", "encodeVideoMsg"));
  document.getElementById("vidDecodeBtn").addEventListener("click", () => decodeFile("video", "decodeVideoFile", "decodeVideoOutput"));

  updateLibrary();
};
