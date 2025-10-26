class VerbatimAI {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.rawTranscript = '';
        this.formattedTranscript = '';
        this.settings = this.loadSettings();
        this.loadModels();
    }

    initializeElements() {
        // Input elements
        this.urlInput = document.getElementById('youtube-url');
        this.getTranscriptBtn = document.getElementById('get-transcript-btn');
        this.formatBtn = document.getElementById('format-btn');

        // Display elements
        this.rawTranscriptArea = document.getElementById('raw-transcript');
        this.formattedTranscriptDiv = document.getElementById('formatted-transcript');
        this.formattedSection = document.getElementById('formatted-section');

        // Loading indicators
        this.rawLoading = document.getElementById('raw-transcript-loading');
        this.formattedLoading = document.getElementById('formatted-transcript-loading');

        // Copy buttons
        this.copyRawBtn = document.getElementById('copy-raw-btn');
        this.copyFormattedBtn = document.getElementById('copy-formatted-btn');

        // Model selection
        this.modelSelect = document.getElementById('model-select');

        // Error display
        this.errorDisplay = document.getElementById('error-display');
        this.errorMessage = document.getElementById('error-message');
        this.errorDismiss = document.getElementById('error-dismiss');

        // Toast
        this.toast = document.getElementById('toast');
        this.toastMessage = document.getElementById('toast-message');

        // Settings modal elements
        this.settingsBtn = document.getElementById('settings-btn');
        this.settingsModal = document.getElementById('settings-modal');

        if (!this.settingsBtn) {
            console.error('Settings button not found!');
        }
        if (!this.settingsModal) {
            console.error('Settings modal not found!');
        }
        this.closeSettingsBtn = document.getElementById('close-settings');
        this.closeSettingsFooterBtn = document.getElementById('close-settings-footer');
        this.apiKeyInput = document.getElementById('api-key-input');
        this.toggleApiKeyBtn = document.getElementById('toggle-api-key');
        this.saveApiKeyBtn = document.getElementById('save-api-key');
        this.clearApiKeyBtn = document.getElementById('clear-api-key');
        this.modelIdInput = document.getElementById('model-id-input');
        this.modelNameInput = document.getElementById('model-name-input');
        this.addModelBtn = document.getElementById('add-model');
        this.customModelsContainer = document.getElementById('custom-models-container');
        this.resetSettingsBtn = document.getElementById('reset-settings');
    }

    bindEvents() {
        this.getTranscriptBtn.addEventListener('click', () => this.fetchTranscript());
        this.formatBtn.addEventListener('click', () => this.formatTranscript());
        this.copyRawBtn.addEventListener('click', () => this.copyToClipboard(this.rawTranscript, 'Raw transcript'));
        this.copyFormattedBtn.addEventListener('click', () => this.copyToClipboard(this.formattedTranscript, 'Formatted transcript'));
        this.errorDismiss.addEventListener('click', () => this.hideError());

        // Settings modal events
        this.settingsBtn.addEventListener('click', () => {
            console.log('Settings button clicked');
            this.openSettings();
        });
        this.closeSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.closeSettingsFooterBtn.addEventListener('click', () => this.closeSettings());
        this.toggleApiKeyBtn.addEventListener('click', () => this.toggleApiKeyVisibility());
        this.saveApiKeyBtn.addEventListener('click', () => this.saveApiKey());
        this.clearApiKeyBtn.addEventListener('click', () => this.clearApiKey());
        this.addModelBtn.addEventListener('click', () => this.addCustomModel());
        this.resetSettingsBtn.addEventListener('click', () => this.resetSettings());

        // Close modal when clicking backdrop
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeSettings();
            }
        });

        // Allow Enter key to trigger transcript fetch
        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.fetchTranscript();
            }
        });

        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to format transcript
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !this.formatBtn.disabled) {
                e.preventDefault();
                this.formatTranscript();
            }

            // Escape to dismiss error
            if (e.key === 'Escape' && !this.errorDisplay.classList.contains('hidden')) {
                this.hideError();
            }
        });
    }

    // Settings management
    loadSettings() {
        const defaultSettings = {
            apiKey: '',
            customModels: []
        };

        try {
            const saved = localStorage.getItem('verbatim-ai-settings');
            return saved ? {...defaultSettings, ...JSON.parse(saved)} : defaultSettings;
        } catch (error) {
            console.error('Failed to load settings:', error);
            return defaultSettings;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('verbatim-ai-settings', JSON.stringify(this.settings));
        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showError('Failed to save settings to browser storage');
        }
    }

    openSettings() {
        console.log('Opening settings modal');
        console.log('Modal element:', this.settingsModal);
        console.log('Modal exists:', !!this.settingsModal);
        console.log('Modal classes before:', this.settingsModal?.className);

        if (!this.settingsModal) {
            console.error('Settings modal element not found!');
            return;
        }

        this.settingsModal.classList.remove('hidden');

        console.log('Modal classes after:', this.settingsModal.className);
        console.log('Modal computed display:', window.getComputedStyle(this.settingsModal).display);
        console.log('Modal computed opacity:', window.getComputedStyle(this.settingsModal).opacity);
        console.log('Modal computed visibility:', window.getComputedStyle(this.settingsModal).visibility);

        this.populateSettingsModal();
        document.body.style.overflow = 'hidden';
    }

    closeSettings() {
        this.settingsModal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    populateSettingsModal() {
        // Load API key (masked)
        this.apiKeyInput.value = this.settings.apiKey ? '••••••••••••••••' : '';
        this.apiKeyInput.dataset.hasKey = this.settings.apiKey ? 'true' : 'false';

        // Load custom models
        this.renderCustomModels();
    }

    toggleApiKeyVisibility() {
        if (this.apiKeyInput.type === 'password') {
            this.apiKeyInput.type = 'text';
            if (this.settings.apiKey && this.apiKeyInput.dataset.hasKey === 'true') {
                this.apiKeyInput.value = this.settings.apiKey;
            }
            this.toggleApiKeyBtn.textContent = '🙈';
        } else {
            this.apiKeyInput.type = 'password';
            if (this.settings.apiKey && this.apiKeyInput.dataset.hasKey === 'true') {
                this.apiKeyInput.value = '••••••••••••••••';
            }
            this.toggleApiKeyBtn.textContent = '👁️';
        }
    }

    saveApiKey() {
        const apiKey = this.apiKeyInput.value.trim();
        if (apiKey && apiKey !== '••••••••••••••••') {
            this.settings.apiKey = apiKey;
            this.saveSettings();
            this.showToast('API key saved successfully!');
            this.apiKeyInput.value = '••••••••••••••••';
            this.apiKeyInput.dataset.hasKey = 'true';
            this.apiKeyInput.type = 'password';
            this.toggleApiKeyBtn.textContent = '👁️';
        }
    }

    clearApiKey() {
        this.settings.apiKey = '';
        this.saveSettings();
        this.apiKeyInput.value = '';
        this.apiKeyInput.dataset.hasKey = 'false';
        this.showToast('API key cleared!');
    }

    addCustomModel() {
        const modelId = this.modelIdInput.value.trim();
        const modelName = this.modelNameInput.value.trim();

        if (!modelId || !modelName) {
            this.showError('Please enter both model ID and display name');
            return;
        }

        // Check if model already exists
        if (this.settings.customModels.find(m => m.id === modelId)) {
            this.showError('Model already exists');
            return;
        }

        // Add model
        this.settings.customModels.push({ id: modelId, name: modelName });
        this.saveSettings();

        // Clear inputs and refresh display
        this.modelIdInput.value = '';
        this.modelNameInput.value = '';
        this.renderCustomModels();
        this.loadModels(); // Refresh the dropdown

        this.showToast('Model added successfully!');
    }

    removeCustomModel(modelId) {
        this.settings.customModels = this.settings.customModels.filter(m => m.id !== modelId);
        this.saveSettings();
        this.renderCustomModels();
        this.loadModels(); // Refresh the dropdown
        this.showToast('Model removed!');
    }

    renderCustomModels() {
        if (this.settings.customModels.length === 0) {
            this.customModelsContainer.innerHTML = '<p style="opacity: 0.6; font-style: italic;">No custom models added yet.</p>';
            return;
        }

        this.customModelsContainer.innerHTML = this.settings.customModels.map(model => `
            <div class="model-item">
                <div class="model-info">
                    <div class="model-name">${model.name}</div>
                    <div class="model-id">${model.id}</div>
                </div>
                <button class="model-remove" onclick="verbatimAI.removeCustomModel('${model.id}')">Remove</button>
            </div>
        `).join('');
    }

    resetSettings() {
        if (confirm('Are you sure you want to reset all settings? This will clear your API key and custom models.')) {
            this.settings = { apiKey: '', customModels: [] };
            this.saveSettings();
            this.populateSettingsModal();
            this.loadModels(); // Refresh the dropdown
            this.showToast('Settings reset successfully!');
        }
    }

    exportSettings() {
        const settingsJson = JSON.stringify(this.settings, null, 2);
        const blob = new Blob([settingsJson], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'verbatim-ai-settings.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        this.showToast('Settings exported successfully');
    }

    importSettings(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedSettings = JSON.parse(e.target.result);
                this.settings = { ...this.settings, ...importedSettings };
                this.saveSettings();
                this.populateSettingsModal();
                this.loadModels();
                this.showToast('Settings imported successfully');
            } catch (error) {
                this.showError('Invalid settings file');
            }
        };
        reader.readAsText(file);
    }

    async loadModels() {
        try {
            const response = await fetch('/static/models.md');
            const text = await response.text();

            const models = [];
            const lines = text.split('\n').filter(line => line.trim());

            for (const line of lines) {
                if (line.includes(':')) {
                    const modelId = line.trim();
                    let displayName = modelId;

                    // Create human-readable names
                    if (modelId.includes('openai/gpt-oss-20b')) {
                        displayName = 'GPT OSS 20B (Free)';
                    } else if (modelId.includes('z-ai/glm-4.5-air')) {
                        displayName = 'GLM 4.5 Air (Free)';
                    } else if (modelId.includes('qwen/qwen3-coder')) {
                        displayName = 'Qwen 3 Coder (Free)';
                    } else if (modelId.includes('moonshotai/kimi-k2')) {
                        displayName = 'Kimi K2 (Free)';
                    } else if (modelId.includes('google/gemma-3n-e2b-it')) {
                        displayName = 'Gemma 3N E2B IT (Free)';
                    } else if (modelId.includes('deepseek/deepseek-r1-0528')) {
                        displayName = 'DeepSeek R1 (Free)';
                    }

                    models.push({ id: modelId, name: displayName });
                }
            }

            // Clear existing options and add new ones
            this.modelSelect.innerHTML = '';

            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = 'anthropic/claude-3.5-sonnet';
            defaultOption.textContent = 'Claude 3.5 Sonnet (Default)';
            defaultOption.selected = true;
            this.modelSelect.appendChild(defaultOption);

            // Add models from file
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.name;
                this.modelSelect.appendChild(option);
            });

            // Add custom models from localStorage
            if (this.settings.customModels.length > 0) {
                const separator = document.createElement('option');
                separator.disabled = true;
                separator.textContent = '--- Custom Models ---';
                this.modelSelect.appendChild(separator);

                this.settings.customModels.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    this.modelSelect.appendChild(option);
                });
            }

        } catch (error) {
            console.error('Failed to load models:', error);
            // Fallback to default models
            this.modelSelect.innerHTML = `
                <option value="anthropic/claude-3.5-sonnet" selected>Claude 3.5 Sonnet (Default)</option>
                <option value="anthropic/claude-3-haiku">Claude 3 Haiku</option>
                <option value="openai/gpt-4o-mini">GPT-4o Mini</option>
            `;
        }
    }


    showError(message) {
        this.errorMessage.textContent = message;
        this.errorDisplay.classList.remove('hidden');

        // Clear existing timeout
        if (this.errorTimeout) {
            clearTimeout(this.errorTimeout);
        }

        // Auto-hide after 15 seconds for better readability
        this.errorTimeout = setTimeout(() => {
            this.hideError();
        }, 15000);
    }

    hideError() {
        this.errorDisplay.classList.add('hidden');
        if (this.errorTimeout) {
            clearTimeout(this.errorTimeout);
            this.errorTimeout = null;
        }
    }

    showToast(message) {
        this.toastMessage.textContent = message;
        this.toast.classList.remove('hidden');

        // Auto-hide after 3 seconds
        setTimeout(() => {
            this.toast.classList.add('hidden');
        }, 3000);
    }

    setLoading(isRaw, isLoading) {
        if (isRaw) {
            if (isLoading) {
                this.rawLoading.classList.remove('hidden');
                this.rawTranscriptArea.classList.add('hidden');
                this.getTranscriptBtn.disabled = true;
                this.getTranscriptBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner"><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/><path d="M12 1v6m0 6v6m11-7h-6m-6 0H1" stroke="currentColor" stroke-width="2"/></svg> Get Transcript';
            } else {
                this.rawLoading.classList.add('hidden');
                this.rawTranscriptArea.classList.remove('hidden');
                this.getTranscriptBtn.disabled = false;
                this.getTranscriptBtn.innerHTML = '<img src="/static/icons/get-transcript.svg" width="16" height="16" class="icon-primary" alt="" /> Get Transcript';
            }
        } else {
            if (isLoading) {
                this.formattedLoading.classList.remove('hidden');
                this.formattedTranscriptDiv.classList.add('hidden');
                this.formatBtn.disabled = true;
                this.formatBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner"><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/><path d="M12 1v6m0 6v6m11-7h-6m-6 0H1" stroke="currentColor" stroke-width="2"/></svg>';
            } else {
                this.formattedLoading.classList.add('hidden');
                this.formattedTranscriptDiv.classList.remove('hidden');
                this.formatBtn.disabled = false;
                this.formatBtn.innerHTML = '<img src="/static/icons/ai.svg" width="16" height="16" class="icon-primary" alt="" />';
            }
        }
    }

    async fetchTranscript() {
        const url = this.urlInput.value.trim();

        if (!url) {
            this.showError('Please enter a YouTube URL');
            return;
        }

        this.hideError();
        this.setLoading(true, true);

        try {
            const response = await fetch('api/transcript', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ youtube_url: url })
            });

            const data = await response.json();

            if (data.success) {
                this.rawTranscript = data.transcript;
                this.rawTranscriptArea.value = this.rawTranscript;
                this.copyRawBtn.disabled = false;
                this.formatBtn.disabled = false;

                // Clear previous formatted result
                this.formattedTranscriptDiv.innerHTML = '<p style="opacity: 0.6; font-style: italic;">Click "Format with AI" to process this transcript...</p>';
                this.copyFormattedBtn.disabled = true;
                this.formattedTranscript = '';
            } else {
                this.showError(data.error || 'Failed to fetch transcript');
                this.rawTranscriptArea.value = '';
                this.copyRawBtn.disabled = true;
                this.formatBtn.disabled = true;
            }
        } catch (error) {
            this.showError('Network error. Please check your connection and try again.');
            console.error('Error fetching transcript:', error);
        } finally {
            this.setLoading(true, false);
        }
    }

    async formatTranscript() {
        if (!this.rawTranscript) {
            this.showError('No transcript available to format');
            return;
        }

        this.hideError();
        this.setLoading(false, true);

        try {
            const selectedModel = this.modelSelect.value;
            const requestBody = {
                raw_transcript: this.rawTranscript,
                model: selectedModel
            };

            // Add API key if stored in settings
            if (this.settings.apiKey) {
                requestBody.api_key = this.settings.apiKey;
            }

            const response = await fetch('api/format', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();

            if (data.success) {
                this.formattedTranscript = data.formatted_transcript;

                // Convert markdown to HTML for better display
                const htmlContent = this.markdownToHtml(this.formattedTranscript);
                this.formattedTranscriptDiv.innerHTML = htmlContent;
                this.copyFormattedBtn.disabled = false;
            } else {
                this.showError(data.error || 'Failed to format transcript');
            }
        } catch (error) {
            this.showError('Network error. Please check your connection and try again.');
            console.error('Error formatting transcript:', error);
        } finally {
            this.setLoading(false, false);
        }
    }

    markdownToHtml(markdown) {
        // Simple markdown to HTML conversion for Beer CSS
        return markdown
            .replace(/^## (.*$)/gim, '<h2 class="formatted-heading">$1</h2>')
            .replace(/^\* (.*$)/gim, '<li>$1</li>')
            .replace(/(<li.*<\/li>)/gs, '<ul class="formatted-list">$1</ul>')
            .replace(/\n\n/g, '</p><p class="formatted-paragraph">')
            .replace(/^(?!<[h|u|l])(.+)$/gm, '<p class="formatted-paragraph">$1</p>')
            .replace(/<p class="formatted-paragraph"><\/p>/g, '');
    }

    async copyToClipboard(text, type) {
        if (!text) {
            this.showError(`No ${type.toLowerCase()} to copy`);
            return;
        }

        try {
            await navigator.clipboard.writeText(text);
            const wordCount = text.split(/\s+/).length;
            const charCount = text.length;
            this.showToast(`${type} copied! ${wordCount} words, ${charCount.toLocaleString()} characters`);
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                const wordCount = text.split(/\s+/).length;
                const charCount = text.length;
                this.showToast(`${type} copied! ${wordCount} words, ${charCount.toLocaleString()} characters`);
            } catch (fallbackError) {
                this.showError('Failed to copy to clipboard');
            }
            document.body.removeChild(textArea);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.verbatimAI = new VerbatimAI();

    // Add debug function to global scope for testing
    window.testModal = function() {
        console.log('Testing modal manually...');
        const modal = document.getElementById('settings-modal');
        if (modal) {
            console.log('Modal found, removing hidden class...');
            modal.classList.remove('hidden');
            console.log('Modal classes:', modal.className);
        } else {
            console.log('Modal not found!');
        }
    };

    // Check for localhost vs IP access and warn about settings differences
    const origin = window.location.origin;
    if (origin.includes('127.0.0.1') || origin.includes('localhost')) {
        console.log(`Note: Settings are stored per origin. localhost and 127.0.0.1 have separate settings.`);
        console.log(`Current origin: ${origin}`);
    }

    console.log('VerbatimAI initialized. Settings button:', document.getElementById('settings-btn'));
    console.log('Settings modal:', document.getElementById('settings-modal'));
});