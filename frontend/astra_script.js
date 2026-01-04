// Astra Nexus - Advanced AI Assistant JavaScript
// Integrates with existing backend while providing futuristic UI interactions

// Execute immediately if DOM is already loaded, otherwise wait for DOMContentLoaded
function initAstra() {
    console.log('Astra: initAstra() called, readyState:', document.readyState);
    // DOM Elements
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const attachBtn = document.getElementById('attach-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const aiStatus = document.getElementById('ai-status');
    const msgCountEl = document.getElementById('msg-count');
    const moodEmojiEl = document.getElementById('mood-emoji');
    const projectList = document.getElementById('project-list');
    const memoryTimeline = document.getElementById('memory-timeline');
    const newChatBtn = document.getElementById('new-chat-btn');
    const uploadZone = document.getElementById('upload-zone');
    const mainVoiceToggle = document.getElementById('voice-output-toggle');

    // Mode buttons
    const modeBtns = document.querySelectorAll('.mode-btn');

    // Suggestion chips
    const suggestionChips = document.querySelectorAll('.suggestion-chip');

    // State
    let currentMode = 'assistant';
    let sessionId = 'session_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
    console.log('Astra: Session ID:', sessionId);
    let messageCount = 0;
    let conversationHistory = [];
    let voiceController = null;
    let isRecording = false;
    let voiceEnabled = true; // Global flag for voice output
    let userName = 'Champ';

    // Initialize
    console.log('Astra: DOMContentLoaded');
    init();

    function init() {
        console.log('Astra: init() started');

        // Handle Splash Screen
        handleSplashScreen();

        // Initialize Voice Controller first
        if (typeof VoiceController !== 'undefined') {
            try {
                console.log('Astra: Initializing VoiceController...');
                voiceController = new VoiceController();
                window.voiceController = voiceController; // Expose to global scope
                console.log('Astra: VoiceController initialized');
            } catch (e) {
                console.error('Astra: VoiceController init failed:', e);
            }
        } else {
            console.warn('Astra: VoiceController is undefined');
        }

        console.log('Astra: Setting up event listeners...');
        setupEventListeners();
        console.log('Astra: Loading projects...');
        loadProjects();
        console.log('Astra: Updating stats...');
        updateStats();

        console.log('Astra: init() completed');
    }

    function handleSplashScreen() {
        const splash = document.getElementById('splash-screen');
        const statusText = document.getElementById('splash-status');
        const particleContainer = document.getElementById('quantum-particles');
        const starfield = document.getElementById('starfield');

        if (!splash) return;

        // Generate Starfield
        for (let i = 0; i < 150; i++) {
            createStar(starfield);
        }

        // Generate Falling Stars
        for (let i = 0; i < 12; i++) {
            createFallingStar(starfield);
        }

        // Generate Stage 1 Particles (Spiraling)
        for (let i = 0; i < 80; i++) {
            createSpiralingParticle(particleContainer);
        }

        const steps = [
            { time: 1500, text: "Quantum particles synchronized." },
            { time: 3000, text: "Neural Core stabilized." },
            { time: 4500, text: "Data streams active." },
            { time: 6000, text: "Neural Nexus established." },
            { time: 7500, text: "Welcome to Astra ML." }
        ];

        steps.forEach(step => {
            setTimeout(() => {
                if (statusText) statusText.textContent = step.text;
            }, step.time);
        });

        setTimeout(() => {
            splash.classList.add('fade-out');
            setTimeout(() => splash.remove(), 1500);
        }, 8500);
    }

    function createStar(container) {
        const star = document.createElement('div');
        star.className = 'star';
        const size = Math.random() * 2;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.setProperty('--duration', `${2 + Math.random() * 3}s`);
        star.style.setProperty('--delay', `${Math.random() * 5}s`);
        container.appendChild(star);
    }

    function createSpiralingParticle(container) {
        const p = document.createElement('div');
        p.className = 'particle';

        const size = Math.random() * 4 + 1;
        const dist = 400 + Math.random() * 300;

        p.style.width = `${size}px`;
        p.style.height = `${size}px`;
        p.style.setProperty('--start-dist', `${dist}px`);

        const duration = 2 + Math.random() * 2;
        const delay = Math.random() * 2;

        p.style.animation = `particle-spiral ${duration}s cubic-bezier(0.4, 0, 0.2, 1) ${delay}s forwards`;

        container.appendChild(p);
    }
        function createFallingStar(container) {
        const star = document.createElement('div');
        star.className = 'falling-star';
        
        // Random start position (top-right quadrant)
        const startX = Math.random() * window.innerWidth + 500;
        const startY = Math.random() * -300;
        
        const travelDist = 1000 + Math.random() * 500;
        const endX = startX - travelDist;
        const endY = startY + travelDist;
        
        star.style.setProperty('--start-x', `${startX}px`);
        star.style.setProperty('--start-y', `${startY}px`);
        star.style.setProperty('--end-x', `${endX}px`);
        star.style.setProperty('--end-y', `${endY}px`);
        
        const duration = 0.6 + Math.random() * 0.8; // Fast zip
        const delay = Math.random() * 8;
        
        star.style.animation = `shooting-star-realistic ${duration}s ease-out ${delay}s infinite`;
        
        container.appendChild(star);
    }

    function createParticle(container) {
        const p = document.createElement('div');
        p.className = 'particle';

        const size = Math.random() * 3 + 1;
        const angle = Math.random() * Math.PI * 2;
        const distance = 300 + Math.random() * 200;

        const startX = Math.cos(angle) * distance;
        const startY = Math.sin(angle) * distance;

        p.style.width = `${size}px`;
        p.style.height = `${size}px`;
        p.style.setProperty('--start-x', `${startX}px`);
        p.style.setProperty('--start-y', `${startY}px`);

        const duration = 1.5 + Math.random() * 1;
        const delay = Math.random() * 1.5;

        p.style.animation = `particle-fly ${duration}s ease-out ${delay}s forwards`;

        container.appendChild(p);
    }


    function setupEventListeners() {
        // Sidebar Toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const leftPanel = document.querySelector('.left-panel');
        const astraPanels = document.querySelector('.astra-panels');

        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                // Desktop behavior
                if (window.innerWidth > 768) {
                    leftPanel.classList.toggle('collapsed');
                    astraPanels.classList.toggle('sidebar-hidden');
                }
                // Mobile behavior
                else {
                    leftPanel.classList.toggle('mobile-open');
                    // Ensure it's visible for animation
                    if (leftPanel.classList.contains('mobile-open')) {
                        leftPanel.style.display = 'flex';
                    }
                }
            });
        }

        // Send message
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Mode switcher
        modeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                modeBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMode = btn.dataset.mode;
                updateStatusText(`${currentMode.charAt(0).toUpperCase() + currentMode.slice(1)} Mode`);



                // Update dynamic suggestions
                updateSuggestions();

                // Add system message about mode switch
                const modeGreetings = {
                    'assistant': "Hello! I'm Astra Assistant. How can I help you today?",
                    'coder': "Astra Coder initialized. Ready to solve complex programming tasks.",
                    'analyst': "Astra Analyst online. Let's dive into your data.",
                    'creative': "Astra Creative mode active. Let's unleash your imagination."
                };
                const greeting = modeGreetings[currentMode] || `Switched to **${currentMode}** mode.`;
                addMessage('system', greeting, 'mode-greeting');
            });
        });

        function updateSuggestions() {
            const suggestionsContainer = document.querySelector('.suggestion-chips');
            if (!suggestionsContainer) return;

            const modeSuggestions = {
                'assistant': [
                    { prompt: 'Tell me a joke', icon: 'fa-laugh' },
                    { prompt: 'What is the weather?', icon: 'fa-cloud-sun' },
                    { prompt: 'Set a reminder', icon: 'fa-clock' }
                ],
                'coder': [
                    { prompt: 'Write a Python loop', icon: 'fa-code' },
                    { prompt: 'Explain recursion', icon: 'fa-brain' },
                    { prompt: 'Debug this JS error', icon: 'fa-bug' }
                ],
                'analyst': [
                    { prompt: 'Analyze this dataset', icon: 'fa-chart-line' },
                    { prompt: 'Summarize the trends', icon: 'fa-file-alt' },
                    { prompt: 'Check for anomalies', icon: 'fa-search-minus' }
                ],
                'creative': [
                    { prompt: 'Write a sci-fi story', icon: 'fa-pen-nib' },
                    { prompt: 'Generate a poem', icon: 'fa-music' },
                    { prompt: 'Design a logo idea', icon: 'fa-paint-brush' }
                ]
            };

            const suggestions = modeSuggestions[currentMode] || modeSuggestions['assistant'];
            suggestionsContainer.innerHTML = '';

            suggestions.forEach(s => {
                const chip = document.createElement('div');
                chip.className = 'suggestion-chip';
                chip.dataset.prompt = s.prompt;
                chip.innerHTML = `<i class="fas ${s.icon}"></i> ${s.prompt}`;
                chip.addEventListener('click', () => {
                    userInput.value = s.prompt;
                    userInput.focus();
                });
                suggestionsContainer.appendChild(chip);
            });
        }

        // Suggestion chips
        suggestionChips.forEach(chip => {
            chip.addEventListener('click', () => {
                userInput.value = chip.dataset.prompt;
                userInput.focus();
            });
        });

        // New chat
        newChatBtn.addEventListener('click', startNewChat);

        // Voice Input
        voiceBtn.addEventListener('click', toggleVoiceInput);

        // File Upload (Simulation)
        attachBtn.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.onchange = handleFileUpload;
            input.click();
        });

        // Drag & Drop Upload
        if (uploadZone) {
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.style.borderColor = 'var(--neon-blue)';
                uploadZone.style.background = 'rgba(0, 212, 255, 0.1)';
            });

            uploadZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadZone.style.borderColor = 'rgba(0, 212, 255, 0.3)';
                uploadZone.style.background = 'rgba(0, 212, 255, 0.05)';
            });

            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.style.borderColor = 'rgba(0, 212, 255, 0.3)';
                uploadZone.style.background = 'rgba(0, 212, 255, 0.05)';

                if (e.dataTransfer.files.length > 0) {
                    handleFileUpload({ target: { files: e.dataTransfer.files } });
                }
            });
        }

        const uploadedFiles = [];
        function handleFileUpload(e) {
            const files = e.target.files;
            if (!files || files.length === 0) return;

            const fileListContainer = document.getElementById('file-list') || createFileContainer();

            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                uploadedFiles.push(file);

                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div class="file-info">
                        <i class="fas fa-file-alt"></i>
                        <span class="file-name">${file.name}</span>
                    </div>
                    <i class="fas fa-times file-remove"></i>
                `;

                fileItem.querySelector('.file-remove').addEventListener('click', () => {
                    fileItem.remove();
                    const index = uploadedFiles.indexOf(file);
                    if (index > -1) uploadedFiles.splice(index, 1);
                });

                fileListContainer.appendChild(fileItem);
            }

            addMessage('system', `Uploaded ${files.length} file(s).`);
        }

        function createFileContainer() {
            const container = document.createElement('div');
            container.id = 'file-list';
            container.className = 'file-list';
            uploadZone.parentNode.appendChild(container);
            return container;
        }


        // Settings Modal
        const settingsBtn = document.getElementById('settings-btn');
        const settingsModal = document.getElementById('settings-modal');
        const closeSettings = document.getElementById('close-settings');

        // New Settings Elements
        const voiceToggle = document.getElementById('voice-toggle');
        const genderToggle = document.getElementById('gender-toggle');
        const themeNeonBtn = document.getElementById('theme-neon');
        const themeLightBtn = document.getElementById('theme-light');
        const themeDarkBtn = document.getElementById('theme-dark');
        const accountBtn = document.getElementById('account-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const testVoiceBtn = document.getElementById('test-voice-btn');
        const activeVoiceName = document.getElementById('active-voice-name');
        const languageSelect = document.getElementById('language-select');

        // Load saved settings
        const savedSettings = JSON.parse(localStorage.getItem('astra_settings') || '{}');
        let currentGender = savedSettings.gender || 'female';
        let currentTheme = savedSettings.theme || 'neon';
        let currentLanguage = savedSettings.language || 'auto';
        voiceEnabled = savedSettings.voiceEnabled !== undefined ? savedSettings.voiceEnabled : true;

        // Apply initial settings
        applyTheme(currentTheme);
        if (genderToggle) genderToggle.checked = (currentGender === 'female');
        if (voiceToggle) voiceToggle.checked = voiceEnabled;
        if (languageSelect) {
            languageSelect.value = currentLanguage;
            // Initialize voice controller with saved language
            if (voiceController) {
                voiceController.setVoice(currentGender, currentLanguage);
            }
        }

        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                settingsModal.classList.add('active');
            });
        }

        if (closeSettings) {
            closeSettings.addEventListener('click', () => {
                settingsModal.classList.remove('active');
            });
        }

        // Voice Handlers
        if (genderToggle) {
            genderToggle.addEventListener('change', (e) => {
                currentGender = e.target.checked ? 'female' : 'male';
                saveSettings({ gender: currentGender });
                if (voiceController && voiceEnabled) {
                    const lang = document.getElementById('language-select').value;
                    voiceController.setVoice(currentGender, lang);
                    updateVoiceStatus();
                    voiceController.speak(`${currentGender.charAt(0).toUpperCase() + currentGender.slice(1)} voice activated.`);
                }
            });
        }

        if (testVoiceBtn) {
            testVoiceBtn.addEventListener('click', () => {
                if (voiceController) {
                    voiceController.unlock();
                    voiceController.testVoice();
                }
            });
        }

        function updateVoiceStatus() {
            if (voiceController && activeVoiceName) {
                const voice = voiceController.selectedVoice;
                if (voice) {
                    activeVoiceName.textContent = voice.name;
                } else if (voiceController.preferredLang !== 'auto') {
                    activeVoiceName.textContent = 'Google Cloud TTS (Fallback)';
                } else {
                    activeVoiceName.textContent = 'System Default';
                }

                // Populate debug list
                const debugList = document.getElementById('available-voices-list');
                if (debugList && voiceController.voices.length > 0) {
                    debugList.innerHTML = voiceController.voices.map(v =>
                        `<div style="padding: 2px 0; border-bottom: 1px solid rgba(255,255,255,0.05); ${v === voiceController.selectedVoice ? 'color: var(--neon-blue); font-weight: bold;' : ''}">
                            ${v.name} (${v.lang})
                        </div>`
                    ).join('');
                } else if (debugList) {
                    debugList.textContent = "No voices detected yet.";
                }
            }
        }

        // Initial voice status
        setTimeout(updateVoiceStatus, 1000);

        if (voiceToggle) {
            voiceToggle.addEventListener('change', (e) => {
                voiceEnabled = e.target.checked;
                saveSettings({ voiceEnabled: voiceEnabled });
                updateMainVoiceToggle();
                if (!voiceEnabled && voiceController) {
                    voiceController.stopSpeaking();
                }
            });
        }

        if (mainVoiceToggle) {
            mainVoiceToggle.addEventListener('click', () => {
                voiceEnabled = !voiceEnabled;
                saveSettings({ voiceEnabled: voiceEnabled });
                if (voiceToggle) voiceToggle.checked = voiceEnabled;
                updateMainVoiceToggle();
                if (!voiceEnabled && voiceController) {
                    voiceController.stopSpeaking();
                }
            });
        }

        function updateMainVoiceToggle() {
            if (mainVoiceToggle) {
                const icon = mainVoiceToggle.querySelector('i');
                if (voiceEnabled) {
                    icon.className = 'fas fa-volume-up';
                    mainVoiceToggle.classList.add('active');
                } else {
                    icon.className = 'fas fa-volume-mute';
                    mainVoiceToggle.classList.remove('active');
                }
            }
        }

        // Initial sync
        updateMainVoiceToggle();

        // Theme Handlers
        if (themeNeonBtn) {
            themeNeonBtn.addEventListener('click', () => {
                applyTheme('neon');
                saveSettings({ theme: 'neon' });
            });
        }

        if (themeLightBtn) {
            themeLightBtn.addEventListener('click', () => {
                applyTheme('light');
                saveSettings({ theme: 'light' });
            });
        }

        if (themeDarkBtn) {
            themeDarkBtn.addEventListener('click', () => {
                applyTheme('dark');
                saveSettings({ theme: 'dark' });
            });
        }

        // Account & Logout
        if (accountBtn) {
            accountBtn.addEventListener('click', () => {
                alert("Account Details:\nUser: ML Enthusiast\nLevel: 5 (Expert)\nPlan: Astra Premium");
            });
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                if (confirm("Are you sure you want to logout?")) {
                    localStorage.removeItem('astra_settings');
                    localStorage.removeItem('chat_history');
                    window.location.reload();
                }
            });
        }



        function updateThemeButtons(theme) {
            if (themeNeonBtn) themeNeonBtn.classList.toggle('active', theme === 'neon');
            if (themeLightBtn) themeLightBtn.classList.toggle('active', theme === 'light');
            if (themeDarkBtn) themeDarkBtn.classList.toggle('active', theme === 'dark');
        }

        function applyTheme(theme) {
            document.body.classList.remove('theme-light', 'theme-dark');
            if (theme === 'light') document.body.classList.add('theme-light');
            if (theme === 'dark') document.body.classList.add('theme-dark');
            updateThemeButtons(theme);
        }

        function saveSettings(newSettings) {
            const current = JSON.parse(localStorage.getItem('astra_settings') || '{}');
            const updated = { ...current, ...newSettings };
            localStorage.setItem('astra_settings', JSON.stringify(updated));
        }

        // Close modal on outside click
        window.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.classList.remove('active');
            }
        });

        // Language Selector
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                const selectedLang = e.target.value;
                const langName = e.target.options[e.target.selectedIndex].text;

                // Update Voice Controller language if available
                if (voiceController) {
                    voiceController.setVoice(currentGender, selectedLang);
                    updateVoiceStatus();
                }

                saveSettings({ language: selectedLang });
                addMessage('system', `Language switched to **${langName}**.`);
            });
        }
    }

    function toggleVoiceInput() {
        if (!voiceController) return;

        if (isRecording) {
            voiceController.stopListening();
            return; // onEnd will handle state cleanup
        }

        isRecording = true;
        voiceBtn.classList.add('recording');
        updateStatusText('Listening...');

        voiceController.startListening(
            (final, interim) => {
                if (interim) {
                    userInput.value = interim;
                }
                if (final) {
                    userInput.value = final;
                    if (voiceController) voiceController.unlock();
                    voiceController.stopListening();
                    sendMessage();
                }
            },
            () => {
                isRecording = false;
                voiceBtn.classList.remove('recording');
                updateStatus('active');
            },
            (error) => {
                isRecording = false;
                voiceBtn.classList.remove('recording');
                updateStatus('active');
                addMessage('system', `Voice Error: ${error}`);
            }
        );
    }

    function handleFileUpload(e) {
        const file = e.target.files[0];
        if (file) {
            addMessage('system', `📁 File uploaded: **${file.name}** (${(file.size / 1024).toFixed(1)} KB)`);
            // Here we would normally upload to server
            setTimeout(() => {
                addMessage('ai', `I've received **${file.name}**. I can analyze this file for you. What would you like to know?`);
            }, 1000);
        }
    }

    async function sendMessage() {
        console.log('sendMessage called');
        const message = userInput.value.trim();
        if (!message) return;

        // Capture target language at the moment of sending
        const targetLang = document.getElementById('language-select').value || 'en';

        // Unlock audio on user gesture (safely)
        if (voiceController && typeof voiceController.unlock === 'function') {
            try {
                voiceController.unlock();
            } catch (e) {
                console.warn('Voice unlock failed:', e);
            }
        }

        // Clear input
        userInput.value = '';

        // Add user message
        addMessage('user', message);

        // Show typing indicator
        showTyping(true);
        updateStatus('thinking');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    session_id: sessionId,
                    target_language: targetLang,
                    mode: currentMode,
                    dataset_context: '' // Could be populated from file upload
                })
            });

            const data = await response.json();

            // Hide typing
            showTyping(false);
            updateStatus('active');

            // Add AI response
            addMessage('ai', data.response || data.error);

            // Speak response if voice is toggled on
            if (voiceController && voiceEnabled && data.response) {
                voiceController.speak(data.response, {
                    lang: targetLang, // Use the language captured at send time
                    onStart: () => updateStatusText('Speaking...'),
                    onEnd: () => updateStatus('active')
                });
            }

            // Update stats
            messageCount += 2;
            updateStats();


            // Add to memory timeline
            addToTimeline(message);

            // Update mood based on sentiment
            if (data.metadata && data.metadata.sentiment) {
                updateMood(data.metadata.sentiment.emotion);
            }

            // Refresh project list (to show updated message count/time)
            loadProjects();

        } catch (error) {
            console.error('Error:', error);
            showTyping(false);
            updateStatus('active');
            addMessage('ai', 'Sorry, I encountered an error. Please try again.');
        }
    }

    function addMessage(role, content, className = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role} ${className}`;

        if (role === 'system') {
            const parsedContent = (typeof marked !== 'undefined') ? marked.parse(content) : content;
            messageDiv.innerHTML = `
                <div class="msg-bubble">
                    <div class="msg-content">${parsedContent}</div>
                </div>
            `;
        } else {
            const avatar = document.createElement('div');
            avatar.className = 'msg-avatar';
            avatar.textContent = role === 'ai' ? '🤖' : '👤';

            const bubble = document.createElement('div');
            bubble.className = 'msg-bubble';

            const msgContent = document.createElement('div');
            msgContent.className = 'msg-content';

            // Use marked for markdown if available, otherwise plain text
            if (typeof marked !== 'undefined') {
                msgContent.innerHTML = marked.parse(content);
            } else {
                msgContent.textContent = content;
            }

            bubble.appendChild(msgContent);
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(bubble);
        }

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Store in conversation history
        if (role !== 'system') {
            conversationHistory.push({ role, content, timestamp: new Date() });
        }
    }

    function showTyping(show) {
        if (show) {
            typingIndicator.classList.remove('hidden');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } else {
            typingIndicator.classList.add('hidden');
        }
    }

    function updateStatus(status) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');

        if (status === 'active') {
            statusDot.style.background = 'var(--neon-blue)';
            statusText.textContent = 'Active';
        } else if (status === 'thinking') {
            statusDot.style.background = 'var(--neon-violet)';
            statusText.textContent = 'Thinking...';
        }
    }

    function updateStatusText(text) {
        document.querySelector('.status-text').textContent = text;
    }

    async function updateStats() {
        if (msgCountEl) msgCountEl.textContent = messageCount;

        try {
            const response = await fetch(`/api/db/analytics/${sessionId}`);
            const data = await response.json();
            if (data && Object.keys(data).length > 0) {
                renderAnalytics(data);
            }
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    }

    function renderAnalytics(data) {
        console.log('Rendering analytics:', data);
        const intentContainer = document.getElementById('intent-distribution');
        const emotionContainer = document.getElementById('emotion-trends');

        if (intentContainer && data.intent_distribution) {
            intentContainer.innerHTML = '';
            const intents = Object.entries(data.intent_distribution);
            if (intents.length === 0) {
                intentContainer.innerHTML = '<div style="font-size:0.7rem; opacity:0.5;">No intent data yet</div>';
            } else {
                const max = Math.max(...intents.map(i => i[1]), 1);
                intents.forEach(([intent, count]) => {
                    const percentage = (count / max) * 100;
                    const row = document.createElement('div');
                    row.className = 'intent-row';
                    row.innerHTML = `
                        <div class="intent-label">
                            <span>${intent}</span>
                            <span>${count}</span>
                        </div>
                        <div class="intent-bar-bg">
                            <div class="intent-bar-fill" style="width: ${percentage}%"></div>
                        </div>
                    `;
                    intentContainer.appendChild(row);
                });
            }
        }

        // Backend returns emotion_distribution, not emotion_trends
        const emotionsData = data.emotion_distribution || data.emotion_trends;
        if (emotionContainer && emotionsData) {
            emotionContainer.innerHTML = '';
            const emotions = Object.entries(emotionsData);
            if (emotions.length === 0) {
                emotionContainer.innerHTML = '<div style="font-size:0.7rem; opacity:0.5;">No emotion data yet</div>';
            } else {
                emotions.forEach(([emotion, count]) => {
                    for (let i = 0; i < Math.min(count, 5); i++) {
                        const dot = document.createElement('div');
                        dot.className = `emotion-dot ${emotion}`;
                        dot.title = `${emotion}: ${count}`;
                        emotionContainer.appendChild(dot);
                    }
                });
                if (emotionContainer.lastChild) {
                    emotionContainer.lastChild.classList.add('active');
                }
            }
        }
    }

    async function executeTool(tool, args) {
        console.log(`Executing tool: ${tool}`, args);
        addMessage('system', `🔧 Executing tool: **${tool}**...`);
        updateStatus('thinking');

        try {
            const response = await fetch(`/api/tools/${tool}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool, args })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Tool response:', data);
            updateStatus('active');

            if (data.error) {
                addMessage('ai', `❌ Tool Error: ${data.error}`);
            } else {
                let resultMsg = `✅ **${data.tool || tool}** execution complete.\n\n`;
                if (data.output) resultMsg += `\`\`\`\n${data.output}\n\`\`\``;
                if (data.results) {
                    resultMsg += "### Search Results:\n";
                    data.results.forEach(res => {
                        resultMsg += `- [${res.title}](${res.url}): ${res.snippet}\n`;
                    });
                }
                if (data.message) resultMsg += data.message;

                addMessage('ai', resultMsg);
            }
        } catch (error) {
            console.error('Tool Error:', error);
            updateStatus('active');
            addMessage('ai', `❌ Sorry, the tool execution failed: ${error.message}`);
        }
    }

    function updateMood(emotion) {
        const moodMap = {
            'positive': '😊',
            'happy': '😄',
            'excited': '🤩',
            'neutral': '😐',
            'confused': '😕',
            'frustrated': '😤',
            'sad': '😢',
            'urgent': '⚡'
        };
        if (moodEmojiEl) moodEmojiEl.textContent = moodMap[emotion] || '😊';
    }

    function addToTimeline(message) {
        if (!memoryTimeline) return;

        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item fade-in';
        timelineItem.textContent = message.substring(0, 40) + (message.length > 40 ? '...' : '');
        timelineItem.title = message;

        memoryTimeline.insertBefore(timelineItem, memoryTimeline.firstChild);

        // Keep only last 10 items
        while (memoryTimeline.children.length > 10) {
            memoryTimeline.removeChild(memoryTimeline.lastChild);
        }
    }

    async function loadProjects() {
        if (!projectList) return;

        try {
            const response = await fetch('/api/db/conversations?limit=5');
            const data = await response.json();

            projectList.innerHTML = '';

            if (data.conversations && data.conversations.length > 0) {
                data.conversations.forEach(conv => {
                    const item = document.createElement('div');
                    item.className = 'project-item';
                    item.style.padding = '10px';
                    item.style.borderBottom = '1px solid rgba(255,255,255,0.1)';
                    item.style.display = 'flex';
                    item.style.justifyContent = 'space-between';
                    item.style.alignItems = 'center';
                    item.style.cursor = 'pointer';

                    const contentDiv = document.createElement('div');
                    contentDiv.innerHTML = `
                        <div style="font-weight:600; font-size:0.9rem; color:white;">${conv.title || 'Untitled Project'}</div>
                        <div style="font-size:0.75rem; color:rgba(255,255,255,0.5);">${new Date(conv.updated_at).toLocaleDateString()} • ${conv.message_count} msgs</div>
                    `;
                    contentDiv.onclick = () => loadSession(conv.id);

                    const deleteBtn = document.createElement('button');
                    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                    deleteBtn.style.background = 'transparent';
                    deleteBtn.style.border = 'none';
                    deleteBtn.style.color = 'rgba(255, 100, 100, 0.7)';
                    deleteBtn.style.cursor = 'pointer';
                    deleteBtn.style.padding = '5px';
                    deleteBtn.onclick = (e) => {
                        e.stopPropagation();
                        deleteProject(conv.id);
                    };

                    item.appendChild(contentDiv);
                    item.appendChild(deleteBtn);
                    projectList.appendChild(item);
                });
            } else {
                projectList.innerHTML = '<div style="padding:10px; color:rgba(255,255,255,0.5); font-size:0.8rem;">No recent projects</div>';
            }
        } catch (error) {
            console.error('Error loading projects:', error);
            projectList.innerHTML = '<div style="padding:10px; color:rgba(255,255,255,0.5); font-size:0.8rem;">Could not load projects</div>';
        }
    }

    async function deleteProject(id) {
        if (!confirm('Are you sure you want to delete this project?')) return;

        try {
            await fetch(`/api/db/conversations/${id}`, { method: 'DELETE' });
            loadProjects();
            if (sessionId === id) {
                startNewChat(false); // Reset if current chat is deleted
            }
        } catch (error) {
            console.error('Error deleting project:', error);
        }
    }

    async function loadSession(id) {
        sessionId = id;
        chatContainer.innerHTML = '';
        conversationHistory = [];

        try {
            const response = await fetch(`/api/db/messages/${id}`);
            const data = await response.json();

            if (data.messages) {
                data.messages.forEach(msg => {
                    addMessage(msg.role, msg.content);
                });
                messageCount = data.messages.length;
                updateStats();

            }
        } catch (error) {
            console.error('Error loading session:', error);
        }
    }

    function startNewChat(askConfirm = true) {
        if (askConfirm && messageCount > 0 && !confirm('Start a new conversation? Current chat is saved.')) {
            return;
        }

        sessionId = 'session_' + Date.now();
        chatContainer.innerHTML = '';
        conversationHistory = [];
        messageCount = 0;
        updateStats();


        // Add initial greeting based on mode
        const modeGreetings = {
            'assistant': "Hello! I'm Astra Assistant. How can I help you today?",
            'coder': "Astra Coder initialized. Ready to solve complex programming tasks.",
            'analyst': "Astra Analyst online. Let's dive into your data.",
            'creative': "Astra Creative mode active. Let's unleash your imagination."
        };
        const greeting = modeGreetings[currentMode] || `Switched to **${currentMode}** mode.`;
        addMessage('system', greeting, 'mode-greeting');
    }


    // Auto-resize textarea
    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Add initial welcome message
    setTimeout(() => {
        if (chatContainer.children.length === 0) {
            addMessage('ai', '👋 Welcome to **Astra Nexus**! I\'m your advanced AI/ML assistant. I can help with:\n\n- 🧠 Machine Learning & Deep Learning\n- 💻 Code writing & debugging\n- 📊 Data analysis & visualization\n- 🎨 Creative solutions\n\nWhat would you like to work on today?');
        }
    }, 500);
}

// Execute immediately if DOM is already loaded, otherwise wait
if (document.readyState === 'loading') {
    console.log('Astra: DOM still loading, adding event listener');
    console.log('Astra: v5.1 Logic Loaded');
    document.addEventListener('DOMContentLoaded', initAstra);
} else {
    console.log('Astra: DOM already loaded, executing immediately');
    console.log('Astra: v5.1 Logic Loaded');
    initAstra();
}
