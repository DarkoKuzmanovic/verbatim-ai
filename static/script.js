class VerbatimAI {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.rawTranscript = '';
        this.formattedTranscript = '';
    }

    initializeElements() {
        // Input elements
        this.urlInput = document.getElementById('youtube-url');
        this.getTranscriptBtn = document.getElementById('get-transcript-btn');
        this.formatBtn = document.getElementById('format-btn');

        // Display elements
        this.rawTranscriptArea = document.getElementById('raw-transcript');
        this.formattedTranscriptDiv = document.getElementById('formatted-transcript');
        
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

        // Toast
        this.toast = document.getElementById('toast');
        this.toastMessage = document.getElementById('toast-message');
    }

    bindEvents() {
        this.getTranscriptBtn.addEventListener('click', () => this.fetchTranscript());
        this.formatBtn.addEventListener('click', () => this.formatTranscript());
        this.copyRawBtn.addEventListener('click', () => this.copyToClipboard(this.rawTranscript, 'Raw transcript'));
        this.copyFormattedBtn.addEventListener('click', () => this.copyToClipboard(this.formattedTranscript, 'Formatted transcript'));
        
        // Allow Enter key to trigger transcript fetch
        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.fetchTranscript();
            }
        });
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorDisplay.classList.remove('hidden');
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            this.errorDisplay.classList.add('hidden');
        }, 10000);
    }

    hideError() {
        this.errorDisplay.classList.add('hidden');
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
                this.rawTranscriptArea.style.display = 'none';
                this.getTranscriptBtn.disabled = true;
                this.getTranscriptBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Fetching...';
            } else {
                this.rawLoading.classList.add('hidden');
                this.rawTranscriptArea.style.display = 'block';
                this.getTranscriptBtn.disabled = false;
                this.getTranscriptBtn.innerHTML = '<i class="fas fa-download mr-2"></i>Get Transcript';
            }
        } else {
            if (isLoading) {
                this.formattedLoading.classList.remove('hidden');
                this.formattedTranscriptDiv.style.display = 'none';
                this.formatBtn.disabled = true;
                this.formatBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Formatting...';
            } else {
                this.formattedLoading.classList.add('hidden');
                this.formattedTranscriptDiv.style.display = 'block';
                this.formatBtn.disabled = false;
                this.formatBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles mr-1"></i>Format with AI';
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
            const response = await fetch('/api/transcript', {
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
                this.formattedTranscriptDiv.innerHTML = '<p class="text-gray-500 italic">Click "Format with AI" to process this transcript...</p>';
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
            
            const response = await fetch('/api/format', {
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
        // Simple markdown to HTML conversion
        return markdown
            .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mb-3 mt-6 text-gray-800">$1</h2>')
            .replace(/^\* (.*$)/gim, '<li class="mb-1">$1</li>')
            .replace(/(<li.*<\/li>)/gs, '<ul class="list-disc pl-5 mb-4">$1</ul>')
            .replace(/\n\n/g, '</p><p class="mb-4">')
            .replace(/^(?!<[h|u|l])(.+)$/gm, '<p class="mb-4">$1</p>')
            .replace(/<p class="mb-4"><\/p>/g, '');
    }

    async copyToClipboard(text, type) {
        if (!text) {
            this.showError(`No ${type.toLowerCase()} to copy`);
            return;
        }

        try {
            await navigator.clipboard.writeText(text);
            this.showToast(`${type} copied to clipboard!`);
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                this.showToast(`${type} copied to clipboard!`);
            } catch (fallbackError) {
                this.showError('Failed to copy to clipboard');
            }
            document.body.removeChild(textArea);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VerbatimAI();
});