document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const uploadButton = document.getElementById('uploadButton');
    const loadingAnimation = document.getElementById('loadingAnimation');
    const capturedImageContainer = document.getElementById('capturedImageContainer');
    const capturedImage = document.getElementById('capturedImage');
    const context = canvas.getContext('2d');
    const toggleSwitch = document.getElementById('toggleSwitch');
    const takePhotoButton = document.getElementById('takePhotoButton');
    const switchCameraButton = document.getElementById('switchCameraButton');
    const enterTextPrompt = document.getElementById('enterTextPrompt');
    const menuBar = document.getElementById('menuBar');
    const toggleMenu = document.getElementById('toggleMenu');
    const focusBox = document.getElementById('focusBox');
    const zoomSlider = document.getElementById('zoomSlider');
    const zoomContainer = document.getElementById('zoomContainer');
    const textPromptModal = document.getElementById('textPromptModal');
    const textPromptInput = document.getElementById('textPrompt');
    const cancelTextPrompt = document.getElementById('cancelTextPrompt');
    const saveTextPrompt = document.getElementById('saveTextPrompt');
    const browserWarningModal = document.getElementById('browserWarningModal');
    const browserWarningOkButton = document.getElementById('browserWarningOkButton');
    let stream = null;
    let imageCapture = null;
    let recognition;
    let audioContext;
    let analyser;
    let microphone;
    let audioWorkletNode;
    let isVoiceMode = localStorage.getItem('isVoiceMode') === 'true';
    let textPrompt = null;
    let zoomLevel = 1;
    let focusBoxTimeout;
    let zoomSliderTimeout;
    let debounceTimeout;
    let isFocusBoxUsed = false;

    const initialize = () => {
        if (!isMobileDevice()) {
            window.location.href = 'https://www.firley.org/products/ecolens-redirect';
        }
        setupEventListeners();
        if (isVoiceMode) {
            startVoiceRecognition();
            toggleSwitch.checked = true;
            switchToVoiceMode();
        } else {
            stopVoiceRecognition();
            toggleSwitch.checked = false;
            switchToCameraMode();
        }
        checkPermissions();
    };

    const isMobileDevice = () => {
        return /Mobi|Android|iPhone|iPad|iPod/.test(navigator.userAgent);
    };

    const checkPermissions = async () => {
        const permissionsGranted = localStorage.getItem('permissionsGranted') === 'true';
        const permissionsGrantedAt = parseInt(localStorage.getItem('permissionsGrantedAt'), 10);
        const thirtyDaysInMilliseconds = 30 * 24 * 60 * 60 * 1000;
        const isPermissionsValid = Date.now() - permissionsGrantedAt < thirtyDaysInMilliseconds;

        if (permissionsGranted && isPermissionsValid) {
            setupMediaStream();
            return;
        }

        try {
            const cameraPermission = await navigator.permissions.query({ name: 'camera' });
            const microphonePermission = await navigator.permissions.query({ name: 'microphone' });

            if (cameraPermission.state === 'granted' && microphonePermission.state === 'granted') {
                setupMediaStream();
            } else {
                requestPermissions();
            }
        } catch (error) {
            console.error('Error checking permissions:', error);
            requestPermissions(); // Fallback to request permissions if check fails
        }
    };

    const requestPermissions = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            if (mediaStream) {
                localStorage.setItem('permissionsGranted', 'true');
                localStorage.setItem('permissionsGrantedAt', Date.now().toString());
                setupMediaStream();
            }
        } catch (error) {
            console.error('Error requesting camera and microphone permissions:', error);
        }
    };

    const setupMediaStream = async () => {
        if (stream) {
            video.srcObject = stream;
            video.play();
            return;
        }

        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } }
            });
            stream = mediaStream;
            video.srcObject = stream;
            video.play();
            imageCapture = new ImageCapture(stream.getVideoTracks()[0]);
            if (isVoiceMode) {
                startAudioProcessing();
            }
        } catch (error) {
            console.error('Error accessing camera: ', error);
        }
    };

    const stopMediaStream = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        if (recognition) {
            recognition.stop();
        }
        if (audioContext) {
            audioContext.close();
        }
        stream = null;
        recognition = null;
        audioContext = null;
    };

    const handleVisibilityChange = () => {
        if (document.hidden) {
            stopMediaStream();
        } else {
            if (localStorage.getItem('permissionsGranted') === 'true') {
                setupMediaStream();
            }
        }
    };

    const captureImageAndSend = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
        if (isFocusBoxUsed) {
            const boxRect = focusBox.getBoundingClientRect();
            const videoRect = video.getBoundingClientRect();
    
            const scaleX = video.videoWidth / videoRect.width;
            const scaleY = video.videoHeight / videoRect.height;
    
            const x = (boxRect.left - videoRect.left) * scaleX;
            const y = (boxRect.top - videoRect.top) * scaleY;
            const size = Math.min(boxRect.width, boxRect.height) * scaleX; // Ensure the box is square
    
            context.strokeStyle = 'red';
            context.lineWidth = 5;
            context.strokeRect(x, y, size, size);
        }
    
        const imageData = canvas.toDataURL('image/jpeg');
        sessionStorage.setItem('capturedImage', imageData);
        displayCapturedImage(imageData);
        sendImageToServer(imageData, textPrompt);
        textPrompt = null;
        isFocusBoxUsed = false;
    };

    const handleImageUpload = (event) => {
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = e.target.result;
            sessionStorage.setItem('capturedImage', imageData);
            displayCapturedImage(imageData);
            sendImageToServer(imageData, textPrompt);
        };
        reader.readAsDataURL(file);
    };

    const sendImageToServer = (imageData, spokenText) => {
        console.log('Sending image and spoken text to server:', spokenText);
        loadingAnimation.style.display = 'flex';
        videoModeToggle.style.display = 'none';
        recordVideoButton.style.display = 'none';

        let photoID = null;

        // Upload the image to get the photo ID
        fetch('/upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData.split(',')[1] })
        })
        .then(response => response.json())
        .then(data => {
            photoID = data.photoID;
            // Proceed with sending the image and spoken text for analysis
            return fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData.split(',')[1], text: spokenText || '', photoID: photoID })
            });
        })
        .then(response => response.json())
        .then(data => {
            data.photoID = photoID;
            sessionStorage.setItem('AIResponse', JSON.stringify(data));
            window.location.href = '/analysis';
        })
        .catch(err => {
            console.error('Error sending image:', err);
            loadingAnimation.style.display = 'none';
        });
    };

    const startVoiceRecognition = () => {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            clearTimeout(debounceTimeout);
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    console.log('Final transcript:', transcript);
                    textPrompt = transcript;
                    stopVoiceRecognition();
                    captureImageAndSend();
                } else {
                    interimTranscript += transcript;
                }
            }
        };

        recognition.onstart = () => {
            startAudioProcessing();
        };

        recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            if (event.error === 'no-speech') {
                if (isVoiceMode) {
                    startVoiceRecognition();
                }
            } else {
                if (event.error !== 'aborted') {
                    startVoiceRecognition();
                }
            }
        };

        recognition.onend = () => {
            console.log('Voice recognition ended');
            if (isVoiceMode && !textPrompt) {
                startVoiceRecognition();
            }
        };

        recognition.start();
    };

    const stopVoiceRecognition = () => {
        if (recognition) {
            recognition.onend = null;
            recognition.stop();
            recognition = null;
        }
        if (audioContext) {
            audioContext.close();
            audioContext = null;
        }
    };

    const startAudioProcessing = async () => {
        if (audioContext) audioContext.close();

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;

        try {
            const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            microphone = audioContext.createMediaStreamSource(audioStream);

            await audioContext.audioWorklet.addModule('voice-processor.js');
            audioWorkletNode = new AudioWorkletNode(audioContext, 'voice-processor');

            microphone.connect(analyser);
            analyser.connect(audioWorkletNode);
            audioWorkletNode.connect(audioContext.destination);

            audioWorkletNode.port.onmessage = (event) => {
                const average = event.data;
                updateVoiceAnimation(average);
            };
        } catch (error) {
            console.error('Error accessing microphone: ', error);
        }
    };

    const updateVoiceAnimation = (volume) => {
        // Update voice animation based on volume (if implemented)
    };

    const toggleMode = () => {
        var userAgent = navigator.userAgent;
        var isWebView = /(iPhone|iPod|iPad|Android).*(AppleWebKit(?!.*Safari)|Version\/4.0 Chrome\/[.0-9]* Mobile Safari\/[.0-9]*$)/.test(userAgent);
    
        // Check if the browser is Safari
        var isSafari = /^((?!chrome|android).)*safari/i.test(userAgent);
    
        if (isWebView || isSafari) {
            // Running in a WebView or Safari, show the browser warning
            toggleSwitch.checked = false;
            showBrowserWarning();
        } else {
            // Not in a WebView or Safari, proceed with normal toggle logic
            isVoiceMode = !isVoiceMode;
            localStorage.setItem('isVoiceMode', isVoiceMode);
            if (isVoiceMode) {
                startVoiceRecognition();
                switchToVoiceMode();
            } else {
                stopVoiceRecognition();
                switchToCameraMode();
            }
        }
    }; 
    

    const switchToVoiceMode = () => {
        document.getElementById('buttonContainerCamera').style.display = 'none';
        capturedImageContainer.style.display = 'none';
        video.style.display = 'block';
    };

    const switchToCameraMode = () => {
        document.getElementById('buttonContainerCamera').style.display = 'flex';
    };

    const showBrowserWarning = () => {
        browserWarningModal.classList.remove('hidden');
    };

    const setupEventListeners = () => {
        toggleSwitch.addEventListener('change', toggleMode);
        uploadButton.addEventListener('change', handleImageUpload);
        takePhotoButton.addEventListener('click', captureImageAndSend);
        switchCameraButton.addEventListener('click', switchCamera);
        enterTextPrompt.addEventListener('click', () => {
            openTextPromptModal();
        });
        cancelTextPrompt.addEventListener('click', closeTextPromptModal);
        saveTextPrompt.addEventListener('click', saveTextPromptModal);
        browserWarningOkButton.addEventListener('click', () => {
            browserWarningModal.classList.add('hidden');
        });

        toggleMenu.addEventListener('click', () => {
            if (menuBar.classList.contains('active')) {
                menuBar.classList.remove('active');
                toggleMenu.classList.remove('down');
                toggleMenu.classList.add('up');
                takePhotoButton.style.bottom = '15vh';
            } else {
                menuBar.classList.add('active');
                toggleMenu.classList.remove('up');
                toggleMenu.classList.add('down');
                takePhotoButton.style.bottom = 'calc(15vh + 5rem)';
            }
        });

        video.addEventListener('click', (event) => {
            console.log("Video was clicked");
            focusBox.style.marginTop = '0vh';
            zoomContainer.style.marginTop = '0vh';
            const rect = video.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            const size = 100; // Size of the square focus box

            focusBox.style.left = `${x - size / 2}px`;
            focusBox.style.top = `${y - size / 2}px`;
            focusBox.style.width = `${size}px`;
            focusBox.style.height = `${size}px`;
            focusBox.style.display = 'block';  // Show focus box

            zoomContainer.style.left = `${x - 100}px`;
            zoomContainer.style.top = `${y + 110}px`;
            zoomContainer.style.display = 'flex';  // Show zoom container
            
            resetFocusBoxTimeout();
            resetZoomSliderTimeout();
            isFocusBoxUsed = true;
        });

        zoomSlider.addEventListener('input', (event) => {
            zoomLevel = event.target.value;
            updateZoom();
            resetZoomSliderTimeout();
        });

        document.addEventListener('visibilitychange', handleVisibilityChange);
    };

    const resetFocusBoxTimeout = () => {
        clearTimeout(focusBoxTimeout);
        focusBoxTimeout = setTimeout(() => {
            focusBox.classList.add('hidden');
        }, 10000);
    };

    const resetZoomSliderTimeout = () => {
        clearTimeout(zoomSliderTimeout);
        zoomSliderTimeout = setTimeout(() => {
            zoomContainer.classList.add('hidden');
        }, 10000);
    };

    const updateZoom = () => {
        const videoRect = video.getBoundingClientRect();
        const boxRect = focusBox.getBoundingClientRect();
        const offsetX = (boxRect.left + boxRect.width / 2) - (videoRect.left + videoRect.width / 2);
        const offsetY = (boxRect.top + boxRect.height / 2) - (videoRect.top + videoRect.height / 2);
        const transformOrigin = `${50 + (offsetX / videoRect.width) * 100}% ${50 + (offsetY / videoRect.height) * 100}%`;
        video.style.transformOrigin = transformOrigin;
        video.style.transform = `scale(${zoomLevel})`;
    };

    const switchCamera = async () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        const constraints = {
            video: { facingMode: (video.getAttribute('data-facing-mode') === 'user' ? 'environment' : 'user') }
        };
        const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
        video.setAttribute('data-facing-mode', constraints.video.facingMode);
        stream = mediaStream;
        video.srcObject = stream;
        video.play();
    };

    const openTextPromptModal = () => {
        textPromptInput.value = textPrompt || '';
        textPromptModal.classList.remove('hidden');
    };

    const closeTextPromptModal = () => {
        textPromptModal.classList.add('hidden');
    };

    const saveTextPromptModal = () => {
        textPrompt = textPromptInput.value;
        closeTextPromptModal();
    };

    const displayCapturedImage = (imageData) => {
        capturedImage.src = imageData;
        capturedImageContainer.style.display = 'flex';
        loadingAnimation.style.display = 'none';
        document.getElementById('buttonContainerCamera').style.display = 'none';
    };

    initialize();
});

document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const videoModeToggle = document.getElementById('videoModeToggle');
    const takePhotoButton = document.getElementById('takePhotoButton');
    const recordVideoButton = document.getElementById('recordVideoButton');
    const loadingAnimation = document.getElementById('loadingAnimation');
    const textPromptInput = document.getElementById('textPrompt');
    let isVideoMode = false;
    let mediaRecorder;
    let recordedChunks = [];
    let stream;

    // Initialize video button as hidden on load
    recordVideoButton.style.display = 'none';

    function getMediaStream() {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (mediaStream) {
            stream = mediaStream;
            video.srcObject = stream;
            video.controls = false; // Disable controls when using camera
            video.play();
        })
        .catch(function (error) {
            console.error("Error accessing media devices.", error);
        });
    }

    function stopMediaStream() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
    }

    function switchToVideoMode() {
        getMediaStream();
        videoModeToggle.innerHTML = '<i class="fas fa-video text-gray-800 text-2xl"></i>';
        takePhotoButton.style.display = 'none';
        recordVideoButton.style.display = 'block';
        isVideoMode = true;
    }

    function switchToCameraMode() {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }
        stopMediaStream();
        videoModeToggle.innerHTML = '<i class="fas fa-camera text-gray-800 text-2xl"></i>';
        takePhotoButton.style.display = 'block';
        recordVideoButton.style.display = 'none';
        isVideoMode = false;
    }

    videoModeToggle.addEventListener('click', () => {
        if (isVideoMode) {
            switchToCameraMode();
        } else {
            switchToVideoMode();
        }
    });

    recordVideoButton.addEventListener('click', () => {
        if (!mediaRecorder || mediaRecorder.state === "inactive") {
            startRecording();
        } else {
            mediaRecorder.stop();
        }
    });

    function startRecording() {
        if (!stream) {
            console.error('No video source available');
            return;
        }
    
        recordedChunks = [];
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm; codecs=vp9' });
    
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
            checkRecordingSize();
        };
    
        mediaRecorder.start();
        console.log('Recording started');
    
        mediaRecorder.onstop = () => {
            console.log('Recording stopped');
            const videoBlob = new Blob(recordedChunks, { type: 'video/webm' });
            const currentDateTime = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `recorded_video_${currentDateTime}.webm`;
            sendVideoToServer(videoBlob, textPromptInput.value, filename);
        };
    }
    
    function checkRecordingSize() {
        const videoBlob = new Blob(recordedChunks, { type: 'video/webm' });
        if (videoBlob.size >= 30000000) { // Check if size is greater than 30 MB
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
                console.log('Recording stopped due to size limit');
            }
        }
    }
    
    function sendVideoToServer(videoBlob, spokenText, filename) {
        console.log('Sending video and spoken text to server:', spokenText);
        loadingAnimation.style.display = 'flex';
    
        let formData = new FormData();
        formData.append('video', videoBlob, filename);
        formData.append('text', spokenText);
    
        fetch('/video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text()) // Changed to text() to handle non-JSON responses
        .then(data => {
            try {
                const jsonData = JSON.parse(data);
                if (jsonData.error) {
                    throw new Error(jsonData.error);
                }
                console.log('Video processing complete:', jsonData);
                sessionStorage.setItem('AIResponse', JSON.stringify(jsonData));
                window.location.href = '/analysis';
            } catch (err) {
                console.error('Error parsing response as JSON:', err);
                throw new Error('Invalid server response');
            }
        })
        .catch(err => {
            console.error('Error sending video:', err);
            loadingAnimation.style.display = 'none';
        });
    }
    
    document.getElementById('videoModeToggle').addEventListener('click', function() {
        var recordButton = document.getElementById('recordVideoButton');
        recordButton.classList.toggle('hidden'); // Toggle visibility when changing modes
    });

    document.getElementById('recordVideoButton').addEventListener('click', function() {
        this.classList.toggle('active'); // Toggle the active class to change appearance
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        } else {
            // Start recording logic here
            console.log('Recording started');
        }
    });
});
