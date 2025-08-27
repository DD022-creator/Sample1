// Handle tab switching
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

// ---------------- Utility ----------------
function capitalize(word) {
    return word.charAt(0).toUpperCase() + word.slice(1);
}

// Style file inputs (make hidden + custom button)
function styleFileInputs() {
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.style.display = "none"; // hide ugly default
    });
}

// Highlight drop zones
function setupDragHighlight(uploadArea) {
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    uploadArea.addEventListener('drop', () => {
        uploadArea.classList.remove('drag-over');
    });
}

// Handle file upload (Image/Audio/Video)
function setupFileUpload(uploadAreaId, fileInputId, previewId, type) {
    const uploadArea = document.getElementById(uploadAreaId);
    const fileInput = document.getElementById(fileInputId);
    const preview = document.getElementById(previewId);

    if (!uploadArea || !fileInput || !preview) return; // prevent crashes if missing

    uploadArea.addEventListener('click', () => fileInput.click());
    setupDragHighlight(uploadArea);

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect(fileInput, preview, type);
        }
    });

    fileInput.addEventListener('change', () => handleFileSelect(fileInput, preview, type));
}

// Show file preview
function handleFileSelect(fileInput, preview, type) {
    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
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

// ---------------- Encode ----------------
async function encodeFile(mode) {
    const fileInput = document.getElementById(`encode${capitalize(mode)}`);
    const secretMessage = document.getElementById(`secretMessage${capitalize(mode)}`).value;

    if (!fileInput || !fileInput.files.length || !secretMessage) {
        alert("Please select a file and enter a secret message.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("secret_message", secretMessage);

    const response = await fetch(`/encode/${mode}`, { method: "POST", body: formData });

    if (!response.ok) {
        alert("Error encoding file");
        return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `stego_${mode}.${mode === "image" ? "png" : mode === "audio" ? "wav" : "avi"}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

// ---------------- Decode ----------------
async function decodeFile(mode) {
    const fileInput = document.getElementById(`decode${capitalize(mode)}`);
    if (!fileInput || !fileInput.files.length) {
        alert("Please select a stego file to decode.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch(`/decode/${mode}`, { method: "POST", body: formData });
    const result = await response.json();

    const msgDiv = document.getElementById(`decodedMessage${capitalize(mode)}`);
    if (msgDiv) {
        msgDiv.innerText = "Secret Message: " + result.secret_message;
    } else {
        alert("Secret Message: " + result.secret_message);
    }
}

// ---------------- Init ----------------
window.onload = () => {
    styleFileInputs();

    // Image
    setupFileUpload("encodeUpload", "encodeImage", "encodePreview", "image");
    setupFileUpload("decodeUpload", "decodeImage", "decodePreview", "image");

    // Audio
    setupFileUpload("audioEncodeUpload", "encodeAudio", "encodeAudioPreview", "audio");
    setupFileUpload("audioDecodeUpload", "decodeAudio", "decodeAudioPreview", "audio");

    // Video
    setupFileUpload("videoEncodeUpload", "encodeVideo", "encodeVideoPreview", "video");
    setupFileUpload("videoDecodeUpload", "decodeVideo", "decodeVideoPreview", "video");
};
