class VoiceController {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isProcessing = false;
        
        this.initializeElements();
        this.initializeSpeechRecognition();
        this.bindEvents();
    }
    
    initializeElements() {
        this.startBtn = document.getElementById('startListening');
        this.stopBtn = document.getElementById('stopListening');
        this.testBtn = document.getElementById('testVoice');
        this.voiceIndicator = document.getElementById('voiceIndicator');
        this.statusText = document.getElementById('statusText');
        this.statusDescription = document.getElementById('statusDescription');
        this.currentCommand = document.getElementById('currentCommand');
        this.commandText = document.getElementById('commandText');
        this.processingStatus = document.getElementById('processingStatus');
        this.responseDisplay = document.getElementById('responseDisplay');
        this.responseText = document.getElementById('responseText');
    }
    
    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.onListeningStart();
            };
            
            this.recognition.onresult = (event) => {
                const command = event.results[0][0].transcript;
                this.onCommandReceived(command);
            };
            
            this.recognition.onerror = (event) => {
                this.onError('Speech recognition error: ' + event.error);
            };
            
            this.recognition.onend = () => {
                this.onListeningEnd();
            };
        } else {
            this.showError('Speech recognition not supported in this browser');
        }
    }
    
    bindEvents() {
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => this.startListening());
        }
        
        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stopListening());
        }
        
        if (this.testBtn) {
            this.testBtn.addEventListener('click', () => this.testVoice());
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (event.key === ' ' && event.ctrlKey) {
                event.preventDefault();
                if (this.isListening) {
                    this.stopListening();
                } else {
                    this.startListening();
                }
            }
        });
    }
    
    startListening() {
        if (!this.recognition) {
            this.showError('Speech recognition not available');
            return;
        }
        
        if (this.isListening || this.isProcessing) {
            return;
        }
        
        try {
            this.recognition.start();
        } catch (error) {
            this.onError('Failed to start listening: ' + error.message);
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }
    
    onListeningStart() {
        this.isListening = true;
        this.updateUI('listening', 'Listening...', 'Speak your command now');
        
        if (this.startBtn) this.startBtn.disabled = true;
        if (this.stopBtn) this.stopBtn.disabled = false;
        
        this.hideAllMessages();
        this.addWaveformAnimation();
    }
    
    onListeningEnd() {
        this.isListening = false;
        this.updateUI('ready', 'Click to start listening', 'Press the microphone to give voice commands');
        
        if (this.startBtn) this.startBtn.disabled = false;
        if (this.stopBtn) this.stopBtn.disabled = true;
        
        this.removeWaveformAnimation();
    }
    
    onCommandReceived(command) {
        this.showCommand(command);
        this.processCommand(command);
    }
    
    async processCommand(command) {
        this.isProcessing = true;
        this.updateUI('processing', 'Processing...', 'Analyzing your command');
        this.showProcessing(true);
        
        try {
            const response = await fetch('/api/process-command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showResponse(result.message);
                this.showToast('Success', result.message, 'success');
            } else {
                this.showError(result.error || 'Command processing failed');
                this.showToast('Error', result.error || 'Command processing failed', 'error');
            }
            
        } catch (error) {
            const errorMsg = 'Network error: ' + error.message;
            this.showError(errorMsg);
            this.showToast('Error', errorMsg, 'error');
        } finally {
            this.isProcessing = false;
            this.showProcessing(false);
            this.updateUI('ready', 'Click to start listening', 'Ready for next command');
        }
    }
    
    async testVoice() {
        try {
            const response = await fetch('/api/voice-test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: 'Voice test successful. System is working properly.' })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('Voice Test', 'Voice system is working properly', 'success');
                this.updateUI('speaking', 'Testing voice...', 'Playing test audio');
                
                setTimeout(() => {
                    this.updateUI('ready', 'Click to start listening', 'Voice test completed');
                }, 3000);
            } else {
                this.showToast('Voice Test Failed', result.error, 'error');
            }
            
        } catch (error) {
            this.showToast('Voice Test Failed', 'Network error: ' + error.message, 'error');
        }
    }
    
    updateUI(state, statusText, description) {
        if (this.statusText) this.statusText.textContent = statusText;
        if (this.statusDescription) this.statusDescription.textContent = description;
        
        if (this.voiceIndicator) {
            this.voiceIndicator.className = 'voice-indicator mx-auto mb-3';
            this.voiceIndicator.classList.add(state);
        }
    }
    
    showCommand(command) {
        if (this.currentCommand && this.commandText) {
            this.commandText.textContent = command;
            this.currentCommand.classList.remove('d-none');
        }
    }
    
    showResponse(response) {
        if (this.responseDisplay && this.responseText) {
            this.responseText.textContent = response;
            this.responseDisplay.classList.remove('d-none');
        }
    }
    
    showProcessing(show) {
        if (this.processingStatus) {
            if (show) {
                this.processingStatus.classList.remove('d-none');
            } else {
                this.processingStatus.classList.add('d-none');
            }
        }
    }
    
    showError(message) {
        this.showToast('Error', message, 'error');
        console.error('Voice Controller Error:', message);
    }
    
    hideAllMessages() {
        if (this.currentCommand) this.currentCommand.classList.add('d-none');
        if (this.responseDisplay) this.responseDisplay.classList.add('d-none');
        if (this.processingStatus) this.processingStatus.classList.add('d-none');
    }
    
    addWaveformAnimation() {
        if (this.voiceIndicator) {
            const waveform = document.createElement('div');
            waveform.className = 'voice-waveform';
            waveform.innerHTML = '<div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>';
            
            const existingWaveform = this.voiceIndicator.querySelector('.voice-waveform');
            if (!existingWaveform) {
                this.voiceIndicator.appendChild(waveform);
            }
        }
    }
    
    removeWaveformAnimation() {
        if (this.voiceIndicator) {
            const waveform = this.voiceIndicator.querySelector('.voice-waveform');
            if (waveform) {
                waveform.remove();
            }
        }
    }
    
    showToast(title, message, type = 'info') {
        const toast = document.getElementById('statusToast');
        const toastTitle = document.getElementById('toastTitle');
        const toastBody = document.getElementById('toastBody');
        const toastIcon = document.getElementById('toastIcon');
        
        if (toast && toastTitle && toastBody && toastIcon) {
            toastTitle.textContent = title;
            toastBody.textContent = message;
            
            // Update icon based on type
            const iconClasses = {
                'success': 'fas fa-check-circle text-success',
                'error': 'fas fa-exclamation-triangle text-danger',
                'warning': 'fas fa-exclamation-circle text-warning',
                'info': 'fas fa-info-circle text-info'
            };
            
            toastIcon.className = iconClasses[type] || iconClasses.info;
            
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }
    
    onError(message) {
        this.isListening = false;
        this.isProcessing = false;
        this.showError(message);
        this.updateUI('ready', 'Click to start listening', 'Error occurred - ready to try again');
        
        if (this.startBtn) this.startBtn.disabled = false;
        if (this.stopBtn) this.stopBtn.disabled = true;
        
        this.showProcessing(false);
        this.removeWaveformAnimation();
    }
}

// Initialize voice controller when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.voiceController = new VoiceController();
    
    // Show initial instructions
    const instructions = [
        "Say 'create a Facebook post about technology' to make a post",
        "Say 'generate an image of a sunset' to create an image",
        "Say 'check auto reply status' to see message status",
        "Say 'how are you' to check system status"
    ];
    
    // Add command suggestions to the page
    setTimeout(() => {
        const suggestions = document.querySelector('.command-suggestions');
        if (suggestions) {
            suggestions.innerHTML = '<h6>Try these commands:</h6>' + 
                instructions.map(cmd => `<span class="suggestion-chip" onclick="window.voiceController.processCommand('${cmd.replace('Say \'', '').replace('\'', '')}')">${cmd}</span>`).join('');
        }
    }, 1000);
});

// Export for global access
window.VoiceController = VoiceController;
