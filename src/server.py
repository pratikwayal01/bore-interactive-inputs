"""
Interactive inputs web server using Flask
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import threading


class InteractiveInputsServer:
    """Flask server for interactive inputs"""
    
    def __init__(self, title: str, fields: List[Dict[str, Any]], timeout: int):
        self.title = title
        self.fields = fields
        self.timeout = timeout
        self.app = Flask(__name__)
        self.results: Optional[Dict[str, Any]] = None
        self.completed = threading.Event()
        self.file_upload_dir = Path("/tmp/bore-interactive-inputs-files")
        self.file_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Store GitHub context for redirects
        self.github_server_url = os.getenv('GITHUB_SERVER_URL', 'https://github.com')
        self.github_repository = os.getenv('GITHUB_REPOSITORY', '')
        self.github_run_id = os.getenv('GITHUB_RUN_ID', '')
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Render the interactive input form"""
            return render_template_string(self._get_html_template())
        
        @self.app.route('/api/config')
        def get_config():
            """Get form configuration"""
            return jsonify({
                'title': self.title,
                'fields': self.fields,
                'timeout': self.timeout
            })
        
        @self.app.route('/api/submit', methods=['POST'])
        def submit():
            """Handle form submission"""
            try:
                data = request.get_json()
                
                # Process file uploads
                processed_data = self._process_submission(data)
                
                self.results = processed_data
                self.completed.set()
                
                # Build workflow URL for redirect
                workflow_url = f"{self.github_server_url}/{self.github_repository}/actions/runs/{self.github_run_id}"
                
                return jsonify({
                    'success': True,
                    'message': 'Inputs submitted successfully',
                    'redirect_url': workflow_url
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
        
        @self.app.route('/api/upload', methods=['POST'])
        def upload():
            """Handle file uploads"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                field_label = request.form.get('field_label')
                
                if not field_label:
                    return jsonify({'error': 'No field label provided'}), 400
                
                # Create directory for this field
                field_dir = self.file_upload_dir / field_label
                field_dir.mkdir(parents=True, exist_ok=True)
                
                # Save file
                filename = file.filename
                filepath = field_dir / filename
                file.save(str(filepath))
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'path': str(filepath)
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    def _process_submission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process submitted data"""
        processed = {}
        
        for field in self.fields:
            label = field.get('label')
            properties = field.get('properties', {})
            field_type = properties.get('type', 'text')
            
            value = data.get(label)
            
            # Handle file/multifile types - return directory path
            if field_type in ['file', 'multifile']:
                field_dir = self.file_upload_dir / label
                if field_dir.exists():
                    processed[label] = str(field_dir)
                else:
                    processed[label] = ''
            else:
                processed[label] = value
        
        return processed
    
    def _get_html_template(self) -> str:
        """Get HTML template for the form"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .field-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .required {
            color: #e74c3c;
            margin-left: 4px;
        }
        
        .description {
            color: #666;
            font-size: 12px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }
        
        .description::before {
            content: 'ℹ';
            display: inline-block;
            width: 16px;
            height: 16px;
            background: #3498db;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 16px;
            margin-right: 6px;
            font-size: 12px;
        }
        
        input[type="text"],
        input[type="number"],
        select,
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus,
        input[type="number"]:focus,
        select:focus,
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        input[type="file"] {
            padding: 10px;
            border: 2px dashed #e0e0e0;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
        }
        
        .multiselect {
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            padding: 10px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .multiselect-option {
            padding: 8px;
            cursor: pointer;
            border-radius: 4px;
            margin-bottom: 4px;
            user-select: none;
        }
        
        .multiselect-option:hover {
            background: #f5f5f5;
        }
        
        .multiselect-option.selected {
            background: #667eea;
            color: white;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 30px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .error {
            color: #e74c3c;
            font-size: 12px;
            margin-top: 4px;
            display: none;
        }
        
        .success-message {
            background: #2ecc71;
            color: white;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
            display: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 10px;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .file-list {
            margin-top: 10px;
            font-size: 12px;
            color: #666;
        }
        
        .file-item {
            background: #f5f5f5;
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .file-remove {
            color: #e74c3c;
            cursor: pointer;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 id="form-title">Loading...</h1>
        <p class="subtitle">Please fill out the form below</p>
        
        <div id="form-container"></div>
        
        <div class="success-message" id="success-message">
            <h2>✓ Submitted Successfully</h2>
            <p>Your inputs have been received.</p>
            <p style="margin-top: 15px;">Redirecting you back to the workflow...</p>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px;">Submitting...</p>
        </div>
    </div>
    
    <script>
        let config = null;
        let uploadedFiles = {};
        
        async function loadConfig() {
            const response = await fetch('/api/config');
            config = await response.json();
            
            document.getElementById('form-title').textContent = config.title;
            renderForm();
        }
        
        function renderForm() {
            const container = document.getElementById('form-container');
            let html = '<form id="interactive-form">';
            
            config.fields.forEach(field => {
                const label = field.label;
                const props = field.properties || {};
                const display = props.display || label;
                const type = props.type || 'text';
                const required = props.required || false;
                const description = props.description || '';
                
                html += `<div class="field-group">`;
                html += `<label>${display}${required ? '<span class="required">*</span>' : ''}</label>`;
                
                if (description) {
                    html += `<div class="description">${description}</div>`;
                }
                
                html += renderField(label, type, props);
                html += `<div class="error" id="error-${label}"></div>`;
                html += `</div>`;
            });
            
            html += '<button type="submit" class="btn">Submit</button>';
            html += '</form>';
            
            container.innerHTML = html;
            
            document.getElementById('interactive-form').addEventListener('submit', handleSubmit);
            
            // Setup file upload handlers
            document.querySelectorAll('input[type="file"]').forEach(input => {
                input.addEventListener('change', handleFileUpload);
            });
            
            // Setup multiselect handlers
            document.querySelectorAll('.multiselect-option').forEach(option => {
                option.addEventListener('click', function() {
                    this.classList.toggle('selected');
                });
            });
        }
        
        function renderField(label, type, props) {
            const defaultValue = props.defaultValue || '';
            const placeholder = props.placeholder || '';
            const readOnly = props.readOnly || false;
            const maxLength = props.maxLength || '';
            const minNumber = props.minNumber !== undefined ? props.minNumber : '';
            const maxNumber = props.maxNumber !== undefined ? props.maxNumber : '';
            const choices = props.choices || [];
            const acceptedFileTypes = props.acceptedFileTypes || [];
            
            switch(type) {
                case 'text':
                    return `<input type="text" name="${label}" id="${label}" 
                            placeholder="${placeholder}" value="${defaultValue}"
                            ${readOnly ? 'readonly' : ''} ${maxLength ? `maxlength="${maxLength}"` : ''}>`;
                
                case 'textarea':
                    return `<textarea name="${label}" id="${label}" 
                            placeholder="${placeholder}" ${readOnly ? 'readonly' : ''}
                            ${maxLength ? `maxlength="${maxLength}"` : ''}>${defaultValue}</textarea>`;
                
                case 'number':
                    return `<input type="number" name="${label}" id="${label}" 
                            placeholder="${placeholder}" value="${defaultValue}"
                            ${minNumber !== '' ? `min="${minNumber}"` : ''}
                            ${maxNumber !== '' ? `max="${maxNumber}"` : ''}>`;
                
                case 'boolean':
                    return `<input type="checkbox" name="${label}" id="${label}" 
                            ${defaultValue === true || defaultValue === 'true' ? 'checked' : ''}>`;
                
                case 'select':
                    let selectHtml = `<select name="${label}" id="${label}">
                                        <option value="">-- Select --</option>`;
                    choices.forEach(choice => {
                        selectHtml += `<option value="${choice}">${choice}</option>`;
                    });
                    selectHtml += `</select>`;
                    return selectHtml;
                
                case 'multiselect':
                    let multiselectHtml = `<div class="multiselect" id="${label}">`;
                    choices.forEach(choice => {
                        multiselectHtml += `<div class="multiselect-option" data-value="${choice}">${choice}</div>`;
                    });
                    multiselectHtml += `</div>`;
                    return multiselectHtml;
                
                case 'file':
                case 'multifile':
                    const accept = acceptedFileTypes.length > 0 ? acceptedFileTypes.join(',') : '*';
                    const multiple = type === 'multifile' ? 'multiple' : '';
                    return `<input type="file" name="${label}" id="${label}" 
                            accept="${accept}" ${multiple} data-label="${label}">
                            <div class="file-list" id="file-list-${label}"></div>`;
                
                default:
                    return `<input type="text" name="${label}" id="${label}">`;
            }
        }
        
        async function handleFileUpload(event) {
            const files = event.target.files;
            const fieldLabel = event.target.dataset.label;
            
            if (!uploadedFiles[fieldLabel]) {
                uploadedFiles[fieldLabel] = [];
            }
            
            for (let file of files) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('field_label', fieldLabel);
                
                try {
                    const response = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        uploadedFiles[fieldLabel].push({
                            filename: result.filename,
                            path: result.path
                        });
                        updateFileList(fieldLabel);
                    }
                } catch (error) {
                    console.error('File upload error:', error);
                }
            }
        }
        
        function updateFileList(fieldLabel) {
            const fileList = document.getElementById(`file-list-${fieldLabel}`);
            if (!fileList) return;
            
            let html = '';
            (uploadedFiles[fieldLabel] || []).forEach((file, index) => {
                html += `<div class="file-item">
                            <span>${file.filename}</span>
                            <span class="file-remove" onclick="removeFile('${fieldLabel}', ${index})">×</span>
                        </div>`;
            });
            fileList.innerHTML = html;
        }
        
        function removeFile(fieldLabel, index) {
            uploadedFiles[fieldLabel].splice(index, 1);
            updateFileList(fieldLabel);
        }
        
        async function handleSubmit(event) {
            event.preventDefault();
            
            // Clear previous errors
            document.querySelectorAll('.error').forEach(el => el.style.display = 'none');
            
            // Collect form data
            const formData = {};
            
            config.fields.forEach(field => {
                const label = field.label;
                const props = field.properties || {};
                const type = props.type || 'text';
                const required = props.required || false;
                
                let value;
                
                if (type === 'boolean') {
                    value = document.getElementById(label).checked;
                } else if (type === 'multiselect') {
                    const selected = [];
                    document.querySelectorAll(`#${label} .multiselect-option.selected`).forEach(opt => {
                        selected.push(opt.dataset.value);
                    });
                    value = selected;
                } else if (type === 'file' || type === 'multifile') {
                    value = uploadedFiles[label] || [];
                } else {
                    value = document.getElementById(label).value;
                }
                
                // Validate required fields
                if (required && !value) {
                    document.getElementById(`error-${label}`).textContent = 'This field is required';
                    document.getElementById(`error-${label}`).style.display = 'block';
                    return;
                }
                
                formData[label] = value;
            });
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.querySelector('.btn').disabled = true;
            
            try {
                const response = await fetch('/api/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('form-container').style.display = 'none';
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('success-message').style.display = 'block';
                    
                    // Redirect to workflow after 3 seconds
                    if (result.redirect_url) {
                        setTimeout(() => {
                            window.location.href = result.redirect_url;
                        }, 3000);
                    }
                } else {
                    alert('Error: ' + result.error);
                    document.getElementById('loading').style.display = 'none';
                    document.querySelector('.btn').disabled = false;
                }
            } catch (error) {
                alert('Submission error: ' + error.message);
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.btn').disabled = false;
            }
        }
        
        // Load configuration on page load
        loadConfig();
    </script>
</body>
</html>
        '''
    
    def run(self, port: int = 5000, debug: bool = False):
        """Run the Flask server"""
        # Disable Flask's reloader and set threaded mode
        self.app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False, threaded=True)
    
    def is_completed(self) -> bool:
        """Check if form has been completed"""
        return self.completed.is_set()
    
    def get_results(self) -> Dict[str, Any]:
        """Get form results"""
        return self.results or {}
