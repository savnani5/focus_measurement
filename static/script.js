const video = document.getElementById('webcam');
let mediaRecorder;
let videoChunks = [];
let stream;
let currentProcessID = null;

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
    // AJAX call to the backend start_processing endpoint
    $.ajax({
        type: 'POST',
        url: '/start_processing',
        success: function(response) {
            console.log('Start processing:', response.message);
            currentProcessID = response.processId;
        },
        error: function(error) {
            console.error('Error starting session:', error);
        }
    });
};

document.getElementById('stopSess').onclick = () => {
    if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
    stopVideoStream();
    // AJAX call to the backend stop_processing endpoint
    $.ajax({
        type: 'POST',
        url: '/stop_processing',
        data: JSON.stringify({ processId: currentProcessID }),
        contentType: 'application/json',
        success: function(response) {
            console.log('Stop processing:', response.message);
        },
        error: function(error) {
            console.error('Error stopping session:', error);
        }
    });
};

function sendVideoToServer() {
    const blob = new Blob(videoChunks, { type: 'video/webm' });
    const formData = new FormData();
    formData.append('video', blob);
    formData.append('processId', currentProcessID); // Include the process ID

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
                highlightFocusLevel(data.focusScore)
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
    }, 2000); // Poll every 3 seconds, adjust as necessary
}

function updateFocusScore(score) {
    document.getElementById('focus-score').textContent = score;
    document.getElementById('progress-container').style.display = 'none';
}

function highlightFocusLevel(decimalScore) {
    // Round the decimal score to the nearest multiple of 20
    let roundedScore = Math.round(decimalScore / 20) * 20;
    roundedScore = Math.max(0, Math.min(roundedScore, 100)); // Ensure it's within 0-100 range

    console.log('roundedScore', roundedScore);

    // // Remove highlight from all levels
    // document.querySelectorAll('.focus-scale-table tr').forEach(tr => {
    //     tr.classList.remove('focus-level-highlight');
    // });

    // Highlight the rounded level
    let currentLevel = document.querySelector(`.focus-scale-table tr[data-score='${roundedScore}']`);
    console.log('Current Level Element:', currentLevel);
    if (currentLevel) {
        currentLevel.classList.add('focus-level-highlight');
    }
}