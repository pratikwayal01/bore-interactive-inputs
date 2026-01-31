# Setup and Usage Guide

This guide will walk you through setting up and using the Bore Interactive Inputs GitHub Action.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Setup](#quick-setup)
3. [Using the Public Bore Server](#using-the-public-bore-server)
4. [Self-Hosting Bore Server](#self-hosting-bore-server)
5. [Configuring Notifications](#configuring-notifications)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- GitHub repository with Actions enabled
- (Optional) Slack workspace with admin access for notifications
- (Optional) Discord server with webhook access for notifications
- (Optional) Server for self-hosting bore (if not using bore.pub)

## Quick Setup

### 1. Add the Action to Your Workflow

Create a workflow file (e.g., `.github/workflows/interactive.yml`):

```yaml
name: Interactive Deployment

on:
  workflow_dispatch:

jobs:
  get-inputs:
    runs-on: ubuntu-latest
    steps:
      - name: Get Deployment Details
        id: inputs
        uses: pratikwayal01/bore-interactive-inputs@v1.0.2
        with:
          bore-server: 'bore.pub'
          title: 'Deployment Configuration'
          interactive: |
            fields:
              - label: environment
                properties:
                  display: Select Environment
                  type: select
                  choices:
                    - development
                    - staging
                    - production
                  required: true
      
      - name: Deploy
        run: |
          echo "Deploying to: ${{ steps.inputs.outputs.environment }}"
```

### 2. Trigger the Workflow

1. Go to your repository on GitHub
2. Click on "Actions" tab
3. Select your workflow
4. Click "Run workflow"
5. Wait for the portal URL to be displayed in the logs
6. Open the URL and fill out the form

## Using the Public Bore Server

The easiest way to get started is using the public bore.pub server:

```yaml
with:
  bore-server: 'bore.pub'
```

**Pros:**
- No setup required
- Free to use
- Maintained by the bore project

**Cons:**
- Public server (less privacy)
- No authentication
- Subject to server availability

## Self-Hosting Bore Server

For better control and privacy, you can host your own bore server.

### 1. Install Bore on Your Server

```bash
# Using Cargo (Rust package manager)
cargo install bore-cli

# Or download pre-built binary
wget https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-x86_64-unknown-linux-musl.tar.gz
tar -xzf bore-v0.6.0-x86_64-unknown-linux-musl.tar.gz
sudo mv bore /usr/local/bin/
```

### 2. Run the Bore Server

**Basic (no authentication):**
```bash
bore server --bind-addr 0.0.0.0
```

**With authentication:**
```bash
bore server --bind-addr 0.0.0.0 --secret your-secret-key
```

**With port restrictions:**
```bash
bore server --bind-addr 0.0.0.0 --min-port 10000 --max-port 20000
```

### 3. Configure Your Workflow

```yaml
with:
  bore-server: 'your-server.com'
  bore-secret: ${{ secrets.BORE_SECRET }}  # if using authentication
```

### 4. Set Up as a Service (Optional)

Create `/etc/systemd/system/bore.service`:

```ini
[Unit]
Description=Bore Tunnel Server
After=network.target

[Service]
Type=simple
User=bore
ExecStart=/usr/local/bin/bore server --bind-addr 0.0.0.0 --secret YOUR_SECRET
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable bore
sudo systemctl start bore
```

## Configuring Notifications

### Slack Notifications

#### 1. Create a Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app and select your workspace
4. Click "Create App"

#### 2. Configure OAuth & Permissions

1. In the left sidebar, click "OAuth & Permissions"
2. Scroll to "Scopes" → "Bot Token Scopes"
3. Add these scopes:
   - `chat:write`
   - `chat:write.customize`
4. Scroll to top and click "Install to Workspace"
5. Authorize the app
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

#### 3. Add Token to GitHub Secrets

1. Go to your repository settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `SLACK_TOKEN`
5. Value: Paste your bot token
6. Click "Add secret"

#### 4. Configure Workflow

```yaml
with:
  notifier-slack-enabled: "true"
  notifier-slack-token: ${{ secrets.SLACK_TOKEN }}
  notifier-slack-channel: "#deployments"
  notifier-slack-bot: "Deploy Bot"
```

#### 5. Send to Thread (Optional)

To reply to a specific thread:

```yaml
with:
  notifier-slack-thread-ts: "1234567890.123456"
```

### Discord Notifications

#### 1. Create a Webhook

1. Go to your Discord server
2. Right-click the channel → "Edit Channel"
3. Click "Integrations" → "Webhooks"
4. Click "New Webhook"
5. Customize name and avatar (optional)
6. Click "Copy Webhook URL"

#### 2. Add Webhook to GitHub Secrets

1. Go to your repository settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `DISCORD_WEBHOOK`
5. Value: Paste your webhook URL
6. Click "Add secret"

#### 3. Configure Workflow

```yaml
with:
  notifier-discord-enabled: "true"
  notifier-discord-webhook: ${{ secrets.DISCORD_WEBHOOK }}
  notifier-discord-username: "Deploy Bot"
```

#### 4. Send to Thread (Optional)

To send to a specific thread:

```yaml
with:
  notifier-discord-thread-id: "1234567890123456789"
```

## Advanced Usage

### File Uploads

```yaml
fields:
  - label: config-files
    properties:
      display: Upload Configuration Files
      type: multifile
      description: Upload JSON or YAML files
      acceptedFileTypes:
        - application/json
        - text/yaml
        - text/yml
      required: true
```

Access uploaded files:

```yaml
- name: Process Files
  run: |
    FILE_DIR="${{ steps.inputs.outputs.config-files }}"
    
    if [ -d "$FILE_DIR" ]; then
      for file in "$FILE_DIR"/*; do
        echo "Processing: $file"
        # Validate and use the file
        cat "$file"
      done
    else
      echo "No files uploaded"
    fi
```

### Conditional Workflows

```yaml
jobs:
  inputs:
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.interactive.outputs.environment }}
      confirmed: ${{ steps.interactive.outputs.confirmed }}
    steps:
      - name: Get Inputs
        id: interactive
        uses: pratikwayal01/bore-interactive-inputs@v1.0.2
        with:
          interactive: |
            fields:
              - label: environment
                properties:
                  type: select
                  choices: [dev, staging, prod]
              - label: confirmed
                properties:
                  type: boolean
  
  deploy-dev:
    needs: inputs
    if: needs.inputs.outputs.environment == 'dev'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to dev"
  
  deploy-prod:
    needs: inputs
    if: needs.inputs.outputs.environment == 'prod' && needs.inputs.outputs.confirmed == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to production"
```

### Dynamic Field Generation

You can generate field choices dynamically:

```yaml
- name: Get Available Versions
  id: versions
  run: |
    # Get versions from API or file
    VERSIONS='["v1.0.0", "v1.1.0", "v2.0.0"]'
    echo "versions=$VERSIONS" >> $GITHUB_OUTPUT

- name: Interactive Input
  uses: pratikwayal01/bore-interactive-inputs@v1.0.2
  with:
    interactive: |
      fields:
        - label: version
          properties:
            type: select
            choices: ${{ steps.versions.outputs.versions }}
```

### Multiple Input Sessions

You can use multiple interactive input steps in one workflow:

```yaml
jobs:
  first-inputs:
    runs-on: ubuntu-latest
    outputs:
      proceed: ${{ steps.inputs.outputs.proceed }}
    steps:
      - id: inputs
        uses: pratikwayal01/bore-interactive-inputs@v1.0.2
        with:
          title: "Step 1: Confirm Deployment"
          interactive: |
            fields:
              - label: proceed
                properties:
                  type: boolean
                  display: Proceed with deployment?
  
  second-inputs:
    needs: first-inputs
    if: needs.first-inputs.outputs.proceed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: pratikwayal01/bore-interactive-inputs@v1.0.2
        with:
          title: "Step 2: Configuration Details"
          interactive: |
            fields:
              - label: config
                properties:
                  type: textarea
                  display: Enter configuration
```

## Troubleshooting

### Portal URL Not Accessible

**Problem:** The portal URL is not loading.

**Solutions:**
1. Check that bore server is running
2. Verify network connectivity to bore server
3. Check firewall rules allow the port
4. Try using bore.pub instead of self-hosted server

### Timeout Errors

**Problem:** Workflow times out before form is submitted.

**Solutions:**
1. Increase timeout value:
   ```yaml
   with:
     timeout: 600  # 10 minutes
   ```
2. Notify users earlier via Slack/Discord
3. Consider workflow_dispatch with manual inputs for simpler cases

### File Upload Issues

**Problem:** Files not uploading or not accessible.

**Solutions:**
1. Check file size limits (default web server limits may apply)
2. Verify accepted file types are correct:
   ```yaml
   acceptedFileTypes:
     - image/*
     - application/pdf
   ```
3. Check file permissions in the uploaded directory

### Slack Notifications Not Working

**Problem:** No Slack notifications received.

**Solutions:**
1. Verify bot token is correct (starts with `xoxb-`)
2. Check bot has required scopes:
   - `chat:write`
   - `chat:write.customize`
3. Verify bot is invited to the channel
4. Check channel name includes `#`: `#deployments`

### Discord Notifications Not Working

**Problem:** No Discord notifications received.

**Solutions:**
1. Verify webhook URL is complete and correct
2. Check webhook hasn't been deleted in Discord
3. For thread messages, verify thread ID is correct
4. Test webhook with curl:
   ```bash
   curl -X POST "$WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"content": "Test message"}'
   ```

### Output Values Not Available

**Problem:** Action outputs are empty in subsequent steps.

**Solutions:**
1. Verify field labels match in workflow:
   ```yaml
   # In interactive config
   - label: my-field
   
   # In next step
   ${{ steps.inputs.outputs.my-field }}
   ```
2. Check form was submitted successfully
3. View action logs for output values

## Getting Help

If you encounter issues:

1. Check action logs for error messages
2. Review this troubleshooting section
3. Search existing GitHub issues
4. Create a new issue with:
   - Workflow YAML
   - Error messages
   - Steps to reproduce

## Best Practices

1. **Use descriptive labels** for better code readability
2. **Add descriptions** to help users understand each field
3. **Set appropriate timeouts** based on expected response time
4. **Enable notifications** for better user experience
5. **Validate inputs** in subsequent steps before using them
6. **Use secrets** for sensitive configuration (bore-secret, tokens)
7. **Test locally** before deploying to production workflows
8. **Document** your interactive inputs in your repository README
