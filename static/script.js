const video = document.getElementById('webcam');
let mediaRecorder;
let videoChunks = [];
let stream;

// Function to start video stream
function startVideoStream() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(s => {
            stream = s;
            video.srcObject = stream;
            video.removeAttribute('hidden'); // Show the video element
            mediaRecorder = new MediaRecorder(stream);
            videoChunks = [];
            mediaRecorder.start();
            mediaRecorder.ondataavailable = e => videoChunks.push(e.data);
            mediaRecorder.onstop = e => sendVideoToServer();
        })
        .catch(err => {
            console.error('Error accessing webcam:', err);
        });
}

// Function to stop video stream
function stopVideoStream() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    video.setAttribute('hidden', ''); // Hide the video element
}

document.getElementById('startSess').onclick = () => {
    startVideoStream();
};

document.getElementById('stopSess').onclick = () => {
    if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
    stopVideoStream();
};

function sendVideoToServer() {
    const blob = new Blob(videoChunks, { type: 'video/webm' });
    const formData = new FormData();
    formData.append('video', blob);

    $.ajax({
        type: 'POST',
        url: '/upload_video',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            console.log('Video successfully sent to server.Process ID:', response.processId);
            document.getElementById('progress-container').style.display = 'block';
            pollForFocusScore(response.processId);
        },
        error: function(error) {
            console.log('Error sending video:', error);
        }
    });
}

function pollForFocusScore(processId) {
    let progress = 0
    const intervalId = setInterval(() => {
        $.get(`/focus_score/${processId}`, function(data, status) {
            if (status === 'success' && data.focusScore !== undefined) {
                clearInterval(intervalId);
                document.getElementById('progress-container').style.display = 'none';
                updateFocusScore(data.focusScore);
            } else if (status === 'error') {
                clearInterval(intervalId);
                console.error('Error fetching focus score');
            } else {
                // Update progress bar
                progress = Math.min(progress + 10, 100); // Increment progress
                document.getElementById('progress-bar').style.width = progress + '%';
            }
            // If still processing, continue polling
        });
    }, 3000); // Poll every 3 seconds, adjust as necessary
}

function updateFocusScore(score) {
    document.getElementById('focus-score').textContent = score;
    document.getElementById('progress-container').style.display = 'none';
}