// Voice UI Controller
// Handles voice input/output using Web Speech API

class VoiceController {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.selectedVoice = null;
        this.voices = [];
        this.utteranceQueue = [];
        this.isSpeakingFlag = false;
        this.currentLang = 'en-US';
        this.preferredGender = 'female';
        this.preferredLang = 'en-US';
        this.audio = new Audio();
        this.isGoogleSpeaking = false;

        this.init();
    }

    init() {
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech Recognition not supported in this browser');
            return;
        }

        // Initialize Speech Recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        // Load voices
        this.loadVoices();
        if (this.synthesis.onvoiceschanged !== undefined) {
            this.synthesis.onvoiceschanged = () => this.loadVoices();
        }
    }

    loadVoices() {
        this.voices = this.synthesis.getVoices();
        // Use preferred settings if voices are loaded
        if (this.voices.length > 0) {
            this.setVoice(this.preferredGender, this.preferredLang);
        }
    }

    setVoice(gender = 'female', language = 'en-US') {
        // Normalize language code (e.g., 'en' -> 'en-US')
        let langCode = language;
        if (language === 'auto') {
            langCode = navigator.language || 'en-US';
        }

        const langMap = {
            'en': 'en-US', 'es': 'es-ES', 'hi': 'hi-IN', 'zh-CN': 'zh-CN',
            'fr': 'fr-FR', 'de': 'de-DE', 'ja': 'ja-JP', 'ko': 'ko-KR',
            'pt': 'pt-BR', 'ru': 'ru-RU', 'it': 'it-IT', 'ar': 'ar-SA',
            'nl': 'nl-NL', 'tr': 'tr-TR', 'pl': 'pl-PL', 'id': 'id-ID',
            'ta': 'ta-IN', 'bn': 'bn-IN', 'te': 'te-IN', 'kn': 'kn-IN',
            'ml': 'ml-IN', 'gu': 'gu-IN', 'mr': 'mr-IN', 'pa': 'pa-IN'
        };

        if (langMap[language]) langCode = langMap[language];

        const voices = this.voices.filter(v => v.lang.startsWith(langCode.split('-')[0]));

        const priorityKeywords = ['Natural', 'Google', 'Microsoft', 'Premium', 'Enhanced'];
        // Expanded male keywords for various languages
        const maleKeywords = [
            'Male', 'David', 'Mark', 'Guy', 'Daniel', // English
            'Pablo', 'Raul', 'Stefan', 'Hemant', 'Ravi', // Spanish, German, Indian
            'Paul', 'Mathieu', 'Jerome', // French
            'Ichiro', 'Haruto', 'Takumi', // Japanese
            'Tae-Theo', 'Min-Ho', // Korean
            'Ivan', 'Pavel', // Russian
            'Ahmet', 'Mehmet', // Turkish
            'Budi', // Indonesian
            'Google US English', 'Microsoft Stefan', 'Microsoft Ravi', 'Microsoft Hemant'
        ];
        const femaleKeywords = ['Female', 'Zira', 'Samantha', 'Google UK English Female', 'Microsoft Kalpana', 'Microsoft Heera', 'Zira', 'Salli', 'Huihui', 'Yaoyao', 'Haruka', 'Ayumi'];

        let bestVoice = null;

        if (voices.length > 0) {
            if (gender === 'female') {
                bestVoice = voices.find(v =>
                    (femaleKeywords.some(k => v.name.includes(k))) &&
                    priorityKeywords.some(k => v.name.includes(k))
                ) || voices.find(v => femaleKeywords.some(k => v.name.includes(k)))
                    || voices[0];
            } else {
                // Male selection logic:
                // 1. Look for explicit male keywords + priority
                // 2. Look for explicit male keywords
                // 3. Look for anything NOT explicitly female (fallback for languages where male names aren't known)
                bestVoice = voices.find(v =>
                    (maleKeywords.some(k => v.name.includes(k))) &&
                    priorityKeywords.some(k => v.name.includes(k))
                ) || voices.find(v => maleKeywords.some(k => v.name.includes(k)))
                    || voices.find(v => !femaleKeywords.some(k => v.name.includes(k)))
                    || voices[0];
            }
        }

        this.selectedVoice = bestVoice;
        this.currentLang = langCode;
        this.preferredGender = gender;
        this.preferredLang = language;

        // Set default pitch based on gender (Male: lower, Female: higher)
        this.defaultPitch = (gender === 'male') ? 0.85 : 1.15;

        if (!this.selectedVoice && language !== 'auto') {
            console.warn(`No specific voice found for ${language}. Falling back to system default.`);
        }

        console.log(`Voice set to: ${this.selectedVoice ? this.selectedVoice.name : 'System Default'} for ${this.currentLang} (Gender: ${gender}, Pitch: ${this.defaultPitch})`);
    }

    testVoice() {
        const testPhrases = {
            'en': 'Hello, I am Astra. Testing my voice output.',
            'hi': 'नमस्ते, मैं एस्ट्रा हूँ। मेरी आवाज़ का परीक्षण कर रहा हूँ।',
            'ta': 'வணக்கம், நான் அஸ்ட்ரா. எனது குரலைச் சோதிக்கிறேன்.',
            'es': 'Hola, soy Astra. Probando mi salida de voz.',
            'fr': 'Bonjour, je suis Astra. Test de ma sortie vocale.',
            'de': 'Hallo, ich bin Astra. Teste meine Sprachausgabe.',
            'zh-CN': '你好，我是 Astra。测试我的语音输出。',
            'ja': 'こんにちは、アストラです。音声出力をテストしています。',
            'auto': 'Hello, testing system default voice.'
        };

        const phrase = testPhrases[this.preferredLang] || testPhrases['en'];
        this.speak(phrase);
    }

    getAvailableVoices() {
        return this.voices.map(v => ({ name: v.name, lang: v.lang }));
    }

    /**
     * Unlocks the audio object by playing a silent sound.
     * Must be called within a user gesture (click, etc.)
     */
    unlock() {
        console.log('VoiceController: Unlocking audio...');
        // Play a tiny silent base64 audio to unlock the main audio object
        const silentSrc = 'data:audio/wav;base64,UklGRigAAABXQVZFWm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==';
        const originalSrc = this.audio.src;
        this.audio.src = silentSrc;
        this.audio.play().then(() => {
            console.log('VoiceController: Audio unlocked successfully.');
            // Restore original src if it was something else (usually empty)
            if (originalSrc && !originalSrc.startsWith('data:')) {
                this.audio.src = originalSrc;
            }
        }).catch(err => {
            console.warn('VoiceController: Audio unlock failed:', err);
        });
    }

    async playGoogleTTS(text, lang) {
        try {
            this.isGoogleSpeaking = true;
            const url = `/api/tts?text=${encodeURIComponent(text)}&lang=${lang}`;
            console.log('VoiceController: Fetching TTS via Proxy:', url);

            const response = await fetch(url);
            if (!response.ok) throw new Error(`TTS Proxy returned ${response.status}`);

            const blob = await response.blob();
            console.log(`VoiceController: Received blob (${blob.size} bytes, type: ${blob.type})`);
            const blobUrl = URL.createObjectURL(blob);

            return new Promise((resolve, reject) => {
                this.audio.src = blobUrl;

                this.audio.onplay = () => {
                    console.log('VoiceController: Audio started playing');
                };

                this.audio.onended = () => {
                    console.log('VoiceController: Audio playback ended');
                    this.isGoogleSpeaking = false;
                    URL.revokeObjectURL(blobUrl);
                    resolve();
                };

                this.audio.onerror = (e) => {
                    this.isGoogleSpeaking = false;
                    const error = this.audio.error;
                    console.error('VoiceController: Audio Object Error:', error ? error.code : 'Unknown', error ? error.message : '');
                    URL.revokeObjectURL(blobUrl);
                    reject(new Error('Audio playback failed.'));
                };

                console.log('VoiceController: Attempting to play audio...');
                this.audio.play().then(() => {
                    console.log('VoiceController: Play promise resolved');
                }).catch(err => {
                    console.error('VoiceController: Audio Play Promise Rejected:', err.name, err.message);
                    this.isGoogleSpeaking = false;
                    URL.revokeObjectURL(blobUrl);
                    reject(err);
                });
            });
        } catch (err) {
            this.isGoogleSpeaking = false;
            console.error('VoiceController: Google TTS Fallback Error:', err);
            throw err;
        }
    }

    startListening(onResult, onEnd, onError) {
        if (!this.recognition || this.isListening) return;

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (onResult) onResult(finalTranscript, interimTranscript);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            if (onEnd) onEnd();
        };

        this.recognition.onerror = (event) => {
            this.isListening = false;
            console.error('Speech recognition error:', event.error);
            if (onError) onError(event.error);
        };

        try {
            this.isListening = true;
            this.recognition.start();
        } catch (e) {
            console.error('Recognition start error:', e);
            this.isListening = false;
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }

    async speak(text, options = {}) {
        this.stopSpeaking();

        const lang = options.lang || this.currentLang;
        const baseLang = lang.split('-')[0];
        console.log(`VoiceController: Speaking in ${lang}`);

        let readableText = text
            .replace(/```(\w+)?\s*([\s\S]*?)```/g, (match, lang, code) => ` Here is the ${lang || ''} code. End of code. `)
            .replace(/`([^`]+)`/g, ' code $1 ')
            .replace(/\$\$([\s\S]*?)\$\$/g, ' The formula is: $1 ')
            .replace(/\$([^$]+)\$/g, ' formula $1 ')
            .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
            .replace(/[*#_]/g, '')
            .replace(/\s+/g, ' ')
            .trim();

        // Check if we should use Google TTS Fallback
        // 1. If language is Tamil (ta) - native support is often poor
        // 2. If no native voice is found for the language
        const needsFallback = baseLang === 'ta' || !this.voices.some(v => v.lang.startsWith(baseLang));

        if (needsFallback) {
            console.log(`VoiceController: Using Google TTS fallback for ${lang}`);
            try {
                if (options.onStart) options.onStart();
                await this.playGoogleTTS(readableText, baseLang);
                if (options.onEnd) options.onEnd();
                return;
            } catch (err) {
                console.error('VoiceController: Fallback failed, trying native anyway:', err);
            }
        }

        // Native Web Speech API Fallback
        if (!this.selectedVoice && this.voices.length > 0) {
            console.warn(`No specific voice found for ${lang}. Using first available voice and pitch-shifting.`);
            this.selectedVoice = this.voices.find(v => v.lang.startsWith(baseLang)) || this.voices[0];
        }

        const sentences = readableText.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [readableText];

        sentences.forEach((sentence, index) => {
            if (!sentence.trim()) return;
            const utterance = new SpeechSynthesisUtterance(sentence.trim());
            utterance.lang = lang;
            if (this.selectedVoice) utterance.voice = this.selectedVoice;

            // PITCH SHIFTING MAGIC
            if (this.preferredGender === 'male' && this.selectedVoice &&
                !this.selectedVoice.name.toLowerCase().includes('male') &&
                !this.selectedVoice.name.toLowerCase().includes('david') &&
                !this.selectedVoice.name.toLowerCase().includes('mark')) {
                utterance.pitch = 0.7;
                utterance.rate = 0.95;
            } else {
                utterance.pitch = options.pitch || this.defaultPitch || 1.0;
                utterance.rate = options.rate || 0.9;
            }

            if (index === 0 && options.onStart) utterance.onstart = options.onStart;
            if (index === sentences.length - 1 && options.onEnd) utterance.onend = options.onEnd;

            this.synthesis.speak(utterance);
        });
    }

    stopSpeaking() {
        this.synthesis.cancel();
        this.audio.pause();
        this.audio.currentTime = 0;
        this.isGoogleSpeaking = false;
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceController;
}
