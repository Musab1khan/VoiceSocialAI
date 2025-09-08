class Dashboard {
    constructor() {
        this.refreshInterval = null;
        this.init();
    }
    
    init() {
        this.setupAutoRefresh();
        this.loadInitialData();
    }
    
    setupAutoRefresh() {
        // Refresh dashboard data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshStats();
        }, 30000);
    }
    
    async loadInitialData() {
        await this.refreshStats();
    }
    
    async refreshStats() {
        try {
            const response = await fetch('/api/system-status');
            const data = await response.json();
            
            if (data.success) {
                this.updateStats(data.status);
                this.updateRecentActivities(data.status);
            } else {
                console.error('Error loading stats:', data.error);
            }
        } catch (error) {
            console.error('Network error loading stats:', error);
        }
    }
    
    updateStats(status) {
        const commandsToday = document.getElementById('commandsToday');
        const repliesToday = document.getElementById('repliesToday');
        const postsToday = document.getElementById('postsToday');
        const systemStatus = document.getElementById('systemStatus');
        
        if (commandsToday) commandsToday.textContent = status.commands_today || 0;
        if (repliesToday) repliesToday.textContent = status.replies_today || 0;
        if (postsToday) postsToday.textContent = status.posts_today || 0;
        if (systemStatus) systemStatus.textContent = 'Online';
    }
    
    updateRecentActivities(status) {
        this.updateCommandsTable(status.recent_commands || []);
        this.updateRepliesTable(status.recent_replies || []);
    }
    
    updateCommandsTable(commands) {
        const tbody = document.getElementById('commandsTable');
        if (!tbody) return;
        
        if (commands.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No recent commands</td></tr>';
            return;
        }
        
        tbody.innerHTML = commands.map(cmd => `
            <tr>
                <td>${this.truncateText(cmd.command_text, 50)}</td>
                <td><span class="badge bg-secondary">${cmd.command_type}</span></td>
                <td>
                    <span class="badge bg-${this.getStatusColor(cmd.status)}">
                        ${cmd.status}
                    </span>
                </td>
                <td><small>${this.formatTime(cmd.created_at)}</small></td>
            </tr>
        `).join('');
    }
    
    updateRepliesTable(replies) {
        const tbody = document.getElementById('repliesTable');
        if (!tbody) return;
        
        if (replies.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No recent replies</td></tr>';
            return;
        }
        
        tbody.innerHTML = replies.map(reply => `
            <tr>
                <td>
                    <i class="${this.getPlatformIcon(reply.platform)} me-1"></i>
                    ${reply.platform}
                </td>
                <td>${this.truncateText(reply.sender, 20)}</td>
                <td><span class="badge bg-success">${reply.status}</span></td>
                <td><small>${this.formatTime(reply.created_at)}</small></td>
            </tr>
        `).join('');
    }
    
    getStatusColor(status) {
        const colors = {
            'completed': 'success',
            'failed': 'danger',
            'processing': 'warning',
            'pending': 'info'
        };
        return colors[status] || 'secondary';
    }
    
    getPlatformIcon(platform) {
        const icons = {
            'email': 'fas fa-envelope',
            'whatsapp': 'fab fa-whatsapp',
            'facebook': 'fab fa-facebook'
        };
        return icons[platform] || 'fas fa-circle';
    }
    
    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    formatTime(isoString) {
        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false
            });
        } catch (error) {
            return 'N/A';
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
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }
}

// Global dashboard functions
async function refreshDashboard() {
    const button = event.target;
    window.dashboard.setButtonLoading(button, true);
    
    try {
        await window.dashboard.refreshStats();
        window.dashboard.showToast('Success', 'Dashboard refreshed successfully', 'success');
    } catch (error) {
        window.dashboard.showToast('Error', 'Failed to refresh dashboard', 'error');
    } finally {
        window.dashboard.setButtonLoading(button, false);
    }
}

async function triggerAutoReply() {
    const button = event.target;
    window.dashboard.setButtonLoading(button, true);
    
    try {
        const response = await fetch('/api/manual-auto-reply', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.dashboard.showToast('Success', result.message, 'success');
            await window.dashboard.refreshStats();
        } else {
            window.dashboard.showToast('Error', result.error, 'error');
        }
    } catch (error) {
        window.dashboard.showToast('Error', 'Network error: ' + error.message, 'error');
    } finally {
        window.dashboard.setButtonLoading(button, false);
    }
}

async function testVoiceSystem() {
    const button = event.target;
    window.dashboard.setButtonLoading(button, true);
    
    try {
        const response = await fetch('/api/voice-test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: 'Dashboard voice test successful' })
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.dashboard.showToast('Voice Test', 'Voice system is working properly', 'success');
        } else {
            window.dashboard.showToast('Voice Test Failed', result.error, 'error');
        }
    } catch (error) {
        window.dashboard.showToast('Voice Test Failed', 'Network error: ' + error.message, 'error');
    } finally {
        window.dashboard.setButtonLoading(button, false);
    }
}

function showCreatePostModal() {
    const modal = new bootstrap.Modal(document.getElementById('createPostModal'));
    modal.show();
}

function showImageGenModal() {
    const modal = new bootstrap.Modal(document.getElementById('imageGenModal'));
    modal.show();
}

async function createPost() {
    const topic = document.getElementById('postTopic').value.trim();
    const includeImage = document.getElementById('includeImage').checked;
    
    if (!topic) {
        window.dashboard.showToast('Error', 'Please enter a topic for the post', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/create-facebook-post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                include_image: includeImage
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.dashboard.showToast('Success', 'Facebook post created successfully', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('createPostModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('postTopic').value = '';
            document.getElementById('includeImage').checked = false;
            
            // Refresh dashboard
            await window.dashboard.refreshStats();
        } else {
            window.dashboard.showToast('Error', result.error, 'error');
        }
    } catch (error) {
        window.dashboard.showToast('Error', 'Network error: ' + error.message, 'error');
    }
}

async function generateImage() {
    const prompt = document.getElementById('imagePrompt').value.trim();
    
    if (!prompt) {
        window.dashboard.showToast('Error', 'Please enter a description for the image', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.dashboard.showToast('Success', 'Image generated successfully', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('imageGenModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('imagePrompt').value = '';
            
            // Show download link
            window.dashboard.showToast('Download', `Image saved: ${result.image_path}`, 'info');
        } else {
            window.dashboard.showToast('Error', result.error, 'error');
        }
    } catch (error) {
        window.dashboard.showToast('Error', 'Network error: ' + error.message, 'error');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
});

// Clean up interval on page unload
window.addEventListener('beforeunload', function() {
    if (window.dashboard && window.dashboard.refreshInterval) {
        clearInterval(window.dashboard.refreshInterval);
    }
});
