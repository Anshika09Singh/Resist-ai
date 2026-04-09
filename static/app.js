const elements = {
    textForm: document.getElementById("textForm"),
    moodText: document.getElementById("moodText"),
    textButton: document.getElementById("textButton"),
    voiceButton: document.getElementById("voiceButton"),
    comboButton: document.getElementById("comboButton"),
    cameraButton: document.getElementById("cameraButton"),
    faceButton: document.getElementById("faceButton"),
    video: document.getElementById("video"),
    statusText: document.getElementById("statusText"),
    statusDot: document.getElementById("statusDot"),
    sourceLabel: document.getElementById("sourceLabel"),
    heroMood: document.getElementById("heroMood"),
    resultCard: document.getElementById("resultCard"),
    errorCard: document.getElementById("errorCard"),
    loadingCard: document.getElementById("loadingCard"),
    loadingText: document.getElementById("loadingText"),
    resultTitle: document.getElementById("resultTitle"),
    resultBadge: document.getElementById("resultBadge"),
    resultText: document.getElementById("resultText"),
    resultMood: document.getElementById("resultMood"),
    resultConfidence: document.getElementById("resultConfidence"),
    resultFaceMood: document.getElementById("resultFaceMood"),
    resultAdvice: document.getElementById("resultAdvice"),
    resultDailyAction: document.getElementById("resultDailyAction"),
    mentalHealthCard: document.getElementById("mentalHealthCard"),
    resultMentalHealth: document.getElementById("resultMentalHealth"),
    suggestionsGrid: document.getElementById("suggestionsGrid"),
    resultLocation: document.getElementById("resultLocation"),
    resultTemp: document.getElementById("resultTemp"),
    resultAqi: document.getElementById("resultAqi"),
};

let activeStream = null;
let activeRecording = null;
let busy = false;
const minimumRecordingMs = 1500;

const buttonLabels = {
    text: "Analyze Text",
    voice: "Start Voice Recording",
    voiceRecording: "Stop and Analyze Voice",
    combo: "Start Combo Analysis",
    comboRecording: "Stop and Analyze Combo",
    camera: "Start Camera",
    face: "Analyze Face",
};

const statusStyles = {
    ready: "bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.9)]",
    working: "bg-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.9)]",
    error: "bg-rose-400 shadow-[0_0_12px_rgba(251,113,133,0.9)]",
};

function setStatus(message, type = "ready") {
    elements.statusText.textContent = message;
    elements.statusDot.className = `mt-1 h-3 w-3 rounded-full ${statusStyles[type] || statusStyles.ready}`;
}

function showError(message) {
    elements.errorCard.textContent = message;
    elements.errorCard.classList.remove("hidden");
}

function clearError() {
    elements.errorCard.classList.add("hidden");
    elements.errorCard.textContent = "";
}

function setLoading(isLoading, message = "Analyzing your input...") {
    elements.loadingText.textContent = message;
    elements.loadingCard.classList.toggle("hidden", !isLoading);
}

function setBusyState(isBusy, message = "") {
    busy = isBusy;
    const shouldDisable = isBusy;

    elements.textButton.disabled = shouldDisable;
    elements.faceButton.disabled = shouldDisable;
    elements.cameraButton.disabled = shouldDisable;

    if (!activeRecording || activeRecording.mode !== "voice") {
        elements.voiceButton.disabled = shouldDisable;
    }
    if (!activeRecording || activeRecording.mode !== "combo") {
        elements.comboButton.disabled = shouldDisable;
    }

    if (message) {
        setStatus(message, isBusy ? "working" : "ready");
        setLoading(isBusy, message);
    } else if (!isBusy) {
        setLoading(false);
    }
}

function setRecordingButton(mode, isRecording) {
    if (mode === "voice") {
        elements.voiceButton.textContent = isRecording ? buttonLabels.voiceRecording : buttonLabels.voice;
        elements.voiceButton.disabled = false;
    }

    if (mode === "combo") {
        elements.comboButton.textContent = isRecording ? buttonLabels.comboRecording : buttonLabels.combo;
        elements.comboButton.disabled = false;
    }
}

function formatSource(source) {
    return source ? source.charAt(0).toUpperCase() + source.slice(1) : "Unknown";
}

function formatTemp(temp) {
    return temp === null || temp === undefined ? "Unavailable" : `${temp} C`;
}

function formatAqi(environment) {
    if (!environment || environment.aqi === null || environment.aqi === undefined) {
        return "Unavailable";
    }
    return `${environment.aqi} (${environment.aqi_category})`;
}

function formatConfidence(score) {
    if (score === null || score === undefined || Number.isNaN(Number(score))) {
        return "Unavailable";
    }
    return `${Number(score).toFixed(1)}%`;
}

function renderSuggestions(suggestions = []) {
    if (!suggestions.length) {
        elements.suggestionsGrid.innerHTML = '<div class="rounded-3xl bg-white border border-slate-200 p-5 text-slate-500">Suggestion cards will appear after analysis.</div>';
        return;
    }

    elements.suggestionsGrid.innerHTML = suggestions
        .map(
            (suggestion) => `
                <div class="rounded-3xl bg-white border border-slate-200 p-5">
                    <p class="text-sm font-semibold text-slate-900">${suggestion.title || "Suggestion"}</p>
                    <p class="mt-2 text-sm leading-6 text-slate-600">${suggestion.description || ""}</p>
                </div>
            `
        )
        .join("");
}

function renderResult(data) {
    const source = formatSource(data.source);
    const mood = data.detected_emotion || data.mood || "Not available";
    const faceMood = data.face_mood || data.raw_face_emotion || "Not available";

    elements.resultCard.classList.remove("hidden");
    elements.resultCard.classList.add("fade-in");
    elements.resultTitle.textContent = `${source} analysis complete`;
    elements.resultBadge.textContent = source;
    elements.resultText.textContent = data.text || "No transcript was produced for this mode.";
    elements.resultMood.textContent = mood;
    elements.resultConfidence.textContent = formatConfidence(data.confidence_score);
    elements.resultFaceMood.textContent = faceMood;
    elements.resultAdvice.textContent = data.advice || "No advice returned.";
    elements.resultDailyAction.textContent = data.daily_action || "No daily action suggestion available.";
    elements.resultLocation.textContent = data.environment?.location || "Unknown";
    elements.resultTemp.textContent = formatTemp(data.environment?.temp);
    elements.resultAqi.textContent = formatAqi(data.environment);
    elements.sourceLabel.textContent = source;
    elements.heroMood.textContent = mood;
    renderSuggestions(data.suggestions || []);

    if (data.mental_health_check) {
        elements.mentalHealthCard.classList.remove("hidden");
        elements.resultMentalHealth.textContent = data.mental_health_check;
    } else {
        elements.mentalHealthCard.classList.add("hidden");
        elements.resultMentalHealth.textContent = "";
    }
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
        throw new Error(data.error || "Request failed.");
    }

    return data;
}

async function ensureCameraStarted() {
    if (activeStream) {
        return activeStream;
    }

    const stream = await navigator.mediaDevices.getUserMedia({
        video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: "user",
        },
    });

    activeStream = stream;
    elements.video.srcObject = stream;
    elements.cameraButton.textContent = "Camera Ready";
    setStatus("Camera is live. You can analyze face or start combo mode.");
    return stream;
}

function captureFrame() {
    if (!activeStream || !elements.video.videoWidth || !elements.video.videoHeight) {
        throw new Error("Start the camera and wait for the preview before capturing a frame.");
    }

    const canvas = document.createElement("canvas");
    canvas.width = elements.video.videoWidth;
    canvas.height = elements.video.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(elements.video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.92);
}

function getSupportedMimeType() {
    const preferred = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/ogg",
        "audio/mp4",
    ];

    return preferred.find((type) => MediaRecorder.isTypeSupported(type)) || "";
}

async function startRecording(mode) {
    if (busy) {
        return;
    }

    if (activeRecording) {
        throw new Error("A recording is already in progress.");
    }

    const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
            echoCancellation: true,
            noiseSuppression: true,
            channelCount: 1,
        },
    });

    const mimeType = getSupportedMimeType();
    const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType, audioBitsPerSecond: 128000 })
        : new MediaRecorder(stream);

    const chunks = [];
    recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
            chunks.push(event.data);
        }
    };

    activeRecording = {
        recorder,
        stream,
        chunks,
        mode,
        startedAt: Date.now(),
    };
    recorder.start();

    setRecordingButton(mode, true);
    setStatus(mode === "combo" ? "Recording combo input. Speak naturally, then tap again to process." : "Listening... Speak clearly, then tap again to process.", "working");
}

function stopActiveRecorder() {
    if (!activeRecording) {
        return null;
    }

    const { recorder, stream, chunks, mode, startedAt } = activeRecording;

    return new Promise((resolve, reject) => {
        let settled = false;

        const finalizeRecording = () => {
            if (settled) {
                return;
            }
            settled = true;

            stream.getTracks().forEach((track) => track.stop());
            activeRecording = null;
            setRecordingButton(mode, false);

            if (Date.now() - startedAt < minimumRecordingMs) {
                reject(new Error("Please record at least 2 seconds of speech before analyzing."));
                return;
            }

            if (!chunks.length) {
                reject(new Error("No audio was captured. Please try again."));
                return;
            }

            const blob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
            if (!blob.size) {
                reject(new Error("The recording was empty. Please try again."));
                return;
            }

            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = () => reject(new Error("Could not read recorded audio."));
            reader.readAsDataURL(blob);
        };

        recorder.onstop = () => {
            setTimeout(finalizeRecording, 60);
        };

        recorder.onerror = () => {
            stream.getTracks().forEach((track) => track.stop());
            activeRecording = null;
            setRecordingButton(mode, false);
            reject(new Error("Audio recording failed."));
        };

        if (recorder.state === "recording") {
            try {
                recorder.requestData();
            } catch (error) {
                console.warn("Recorder requestData() was not supported for this browser.", error);
            }
        }

        recorder.stop();
    });
}

async function handleTextSubmit(event) {
    event.preventDefault();
    clearError();

    const text = elements.moodText.value.trim();
    if (!text) {
        showError("Please type a message before running text analysis.");
        setStatus("Text input is required for analysis.", "error");
        return;
    }

    try {
        setBusyState(true, "Processing text analysis...");
        const data = await postJson("/analyze/text", { text });
        renderResult(data);
        setStatus("Text analysis complete.");
    } catch (error) {
        showError(error.message);
        setStatus(error.message, "error");
    } finally {
        setBusyState(false);
    }
}

async function toggleVoiceAnalysis() {
    clearError();

    try {
        if (activeRecording?.mode === "voice") {
            setBusyState(true, "Processing voice recording...");
            const audio = await stopActiveRecorder();
            const data = await postJson("/analyze/voice", { audio });
            renderResult(data);
            setStatus("Voice analysis complete.");
            return;
        }

        if (activeRecording) {
            throw new Error("Finish the current recording before starting voice mode.");
        }

        await startRecording("voice");
        elements.comboButton.disabled = true;
    } catch (error) {
        showError(error.message);
        setStatus(error.message, "error");
    } finally {
        if (!activeRecording) {
            setBusyState(false);
        }
        if (!activeRecording) {
            elements.comboButton.disabled = false;
        }
    }
}

async function handleCameraStart() {
    clearError();

    try {
        setBusyState(true, "Starting camera...");
        await ensureCameraStarted();
    } catch (error) {
        showError("Camera access failed. Please allow permission and try again.");
        setStatus("Camera access failed. Please allow permission and try again.", "error");
    } finally {
        setBusyState(false);
    }
}

async function handleFaceAnalysis() {
    clearError();

    try {
        setBusyState(true, "Capturing frame and analyzing face...");
        await ensureCameraStarted();
        const image = captureFrame();
        const data = await postJson("/analyze/face", { image });
        renderResult(data);
        setStatus("Face analysis complete.");
    } catch (error) {
        showError(error.message);
        setStatus(error.message, "error");
    } finally {
        setBusyState(false);
    }
}

async function toggleComboAnalysis() {
    clearError();

    try {
        if (activeRecording?.mode === "combo") {
            setBusyState(true, "Processing combo analysis...");
            const audio = await stopActiveRecorder();
            const image = captureFrame();
            const data = await postJson("/analyze/combo", { audio, image });
            renderResult(data);
            setStatus("Combo analysis complete.");
            return;
        }

        if (activeRecording) {
            throw new Error("Finish the current recording before starting combo mode.");
        }

        await ensureCameraStarted();
        await startRecording("combo");
        elements.voiceButton.disabled = true;
    } catch (error) {
        showError(error.message);
        setStatus(error.message, "error");
    } finally {
        if (!activeRecording) {
            setBusyState(false);
            elements.voiceButton.disabled = false;
        }
    }
}

elements.textForm.addEventListener("submit", handleTextSubmit);
elements.voiceButton.addEventListener("click", toggleVoiceAnalysis);
elements.comboButton.addEventListener("click", toggleComboAnalysis);
elements.cameraButton.addEventListener("click", handleCameraStart);
elements.faceButton.addEventListener("click", handleFaceAnalysis);

window.addEventListener("beforeunload", () => {
    if (activeStream) {
        activeStream.getTracks().forEach((track) => track.stop());
    }
    if (activeRecording?.stream) {
        activeRecording.stream.getTracks().forEach((track) => track.stop());
    }
});
