# Bore Interactive Inputs

A GitHub Action that enables dynamic runtime user inputs for workflows using self-hosted [bore](https://github.com/ekzhang/bore) tunnels instead of ngrok. This action allows you to create interactive input portals with various field types including text, files, multi-select, and more.

## Features

- 🔒 **Self-hosted bore tunnel** - Use your own bore server or the public bore.pub
- 📝 **Multiple input types** - text, textarea, number, boolean, select, multiselect, file, multifile
- 🔔 **Slack & Discord notifications** - Get notified when inputs are needed
- 📁 **File upload support** - Upload files during workflow execution
- ⚙️ **Fully configurable** - All options available through action inputs
- 🐍 **Python-based** - Easy to maintain and extend

## Quick Start

### Basic Example

```yaml
name: Interactive Input Example

on:
  workflow_dispatch:

jobs:
  interactive:
    runs-on: ubuntu-latest
    steps:
      - name: Get User Input
        id: inputs
        uses: pratikwayal01/bore-interactive-inputs@v1
        with:
          bore-server: 'bore.pub'  # or your self-hosted server
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
              
              - label: deploy-message
                properties:
                  display: Deployment Message
                  type: text
                  placeholder: Enter deployment message
                  required: true
      
      - name: Use Inputs
        run: |
          echo "Environment: ${{ steps.inputs.outputs.environment }}"
          echo "Message: ${{ steps.inputs.outputs.deploy-message }}"
```

## Installation

1. Add this action to your repository
2. Set up a bore server (or use bore.pub)
3. Configure your workflow file

## Input Options

### Core Configuration

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `title` | Title of the interactive form | No | `Interactive Inputs` |
| `interactive` | YAML definition of input fields | Yes | - |
| `timeout` | Timeout in seconds | No | `300` |
| `bore-server` | Bore server address | Yes | `bore.pub` |
| `bore-port` | Specific port to request | No | `0` (random) |
| `bore-secret` | Authentication secret | No | - |
| `github-token` | GitHub token | Yes | `${{ github.token }}` |

### Slack Notifications

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `notifier-slack-enabled` | Enable Slack notifications | No | `false` |
| `notifier-slack-token` | Slack bot token | Conditional | - |
| `notifier-slack-channel` | Slack channel | No | `#notifications` |
| `notifier-slack-thread-ts` | Thread timestamp | No | - |
| `notifier-slack-bot` | Bot display name | No | `Bore Interactive Inputs` |

### Discord Notifications

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `notifier-discord-enabled` | Enable Discord notifications | No | `false` |
| `notifier-discord-webhook` | Discord webhook URL | Conditional | - |
| `notifier-discord-thread-id` | Thread ID | No | - |
| `notifier-discord-username` | Username display | No | `Bore Interactive Inputs` |

## Field Types

### Text Input

```yaml
- label: username
  properties:
    display: Username
    type: text
    placeholder: Enter username
    maxLength: 50
    required: true
```

### Textarea Input

```yaml
- label: description
  properties:
    display: Description
    type: textarea
    placeholder: Enter description
    maxLength: 500
    readOnly: false
```

### Number Input

```yaml
- label: quantity
  properties:
    display: Quantity
    type: number
    minNumber: 1
    maxNumber: 100
    required: true
```

### Boolean Input

```yaml
- label: confirmed
  properties:
    display: Confirm deployment?
    type: boolean
    defaultValue: false
```

### Select Input

```yaml
- label: region
  properties:
    display: Select Region
    type: select
    choices:
      - us-east-1
      - us-west-2
      - eu-west-1
    required: true
```

### Multi-Select Input

```yaml
- label: features
  properties:
    display: Select Features
    type: multiselect
    choices:
      - Feature A
      - Feature B
      - Feature C
    required: false
```

### File Input

```yaml
- label: config-file
  properties:
    display: Upload Configuration
    type: file
    acceptedFileTypes:
      - application/json
      - text/yaml
    required: true
```

### Multi-File Input

```yaml
- label: documents
  properties:
    display: Upload Documents
    type: multifile
    acceptedFileTypes:
      - application/pdf
      - image/*
    required: false
```

## Complete Example

```yaml
name: Advanced Interactive Workflow

on:
  workflow_dispatch:

jobs:
  interactive-inputs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      actions: write
    steps:
      - name: Interactive Inputs
        id: inputs
        uses: pratikwayal01/bore-interactive-inputs@v1
        with:
          bore-server: 'bore.pub'
          timeout: 600
          title: 'Production Deployment'
          interactive: |
            fields:
              - label: environment
                properties:
                  display: Target Environment
                  type: select
                  description: Select the deployment environment
                  choices:
                    - staging
                    - production
                  required: true
              
              - label: version
                properties:
                  display: Version Number
                  type: text
                  placeholder: e.g., v1.2.3
                  required: true
              
              - label: release-notes
                properties:
                  display: Release Notes
                  type: textarea
                  placeholder: Describe the changes
                  maxLength: 1000
              
              - label: migration-files
                properties:
                  display: Upload Migration Scripts
                  type: multifile
                  description: Upload any database migration files
                  acceptedFileTypes:
                    - text/sql
                    - application/sql
              
              - label: notify-users
                properties:
                  display: Send user notifications?
                  type: boolean
                  defaultValue: true
              
              - label: rollback-plan
                properties:
                  display: Rollback Plan Confirmed?
                  type: boolean
                  required: true
          
          notifier-slack-enabled: "true"
          notifier-slack-token: ${{ secrets.SLACK_TOKEN }}
          notifier-slack-channel: "#deployments"
          
          notifier-discord-enabled: "true"
          notifier-discord-webhook: ${{ secrets.DISCORD_WEBHOOK }}
    
    outputs:
      environment: ${{ steps.inputs.outputs.environment }}
      version: ${{ steps.inputs.outputs.version }}
      release-notes: ${{ steps.inputs.outputs.release-notes }}
      migration-files: ${{ steps.inputs.outputs.migration-files }}
      notify-users: ${{ steps.inputs.outputs.notify-users }}
      rollback-plan: ${{ steps.inputs.outputs.rollback-plan }}

  deploy:
    needs: interactive-inputs
    runs-on: ubuntu-latest
    steps:
      - name: Deploy Application
        run: |
          echo "Deploying to: ${{ needs.interactive-inputs.outputs.environment }}"
          echo "Version: ${{ needs.interactive-inputs.outputs.version }}"
          echo "Release notes: ${{ needs.interactive-inputs.outputs.release-notes }}"
          echo "Notify users: ${{ needs.interactive-inputs.outputs.notify-users }}"
          
          # Process migration files if uploaded
          if [ -d "${{ needs.interactive-inputs.outputs.migration-files }}" ]; then
            echo "Migration files found:"
            ls -la "${{ needs.interactive-inputs.outputs.migration-files }}"
          fi
```

## Setting Up Slack Notifications

1. Create a Slack app at https://api.slack.com/apps
2. Add the following bot token scopes:
   - `chat:write`
   - `chat:write.customize`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token
5. Add it as a secret `SLACK_TOKEN` in your repository

## Setting Up Discord Notifications

1. Go to your Discord server settings
2. Navigate to Integrations → Webhooks
3. Create a new webhook
4. Copy the webhook URL
5. Add it as a secret `DISCORD_WEBHOOK` in your repository

## Self-Hosting Bore Server

To self-host your own bore server:

```bash
# Install bore
cargo install bore-cli

# Run the server
bore server --bind-addr 0.0.0.0

# Optional: with authentication
bore server --secret your-secret-key
```

Then use your server address in the workflow:

```yaml
with:
  bore-server: 'your-server.com'
  bore-secret: ${{ secrets.BORE_SECRET }}
```

## How It Works

1. Action starts a Flask web server with your interactive form
2. Bore tunnel is established to expose the server
3. Notifications are sent with the portal URL
4. User fills out the form
5. Results are captured and set as action outputs
6. Workflow continues with the user's inputs

## Output Format

- **Text fields**: String value
- **Number fields**: Numeric value
- **Boolean fields**: `true` or `false`
- **Select fields**: Selected option string
- **Multiselect fields**: JSON array of selected options
- **File/Multifile fields**: Directory path containing uploaded files

## Accessing Uploaded Files

```yaml
- name: Process Uploaded Files
  run: |
    # File uploads are stored in a directory
    FILE_DIR="${{ steps.inputs.outputs.my-file-field }}"
    
    if [ -d "$FILE_DIR" ]; then
      echo "Processing files in $FILE_DIR"
      for file in "$FILE_DIR"/*; do
        echo "Processing: $file"
        # Do something with each file
      done
    fi
```

## Comparison with interactive-inputs

| Feature | interactive-inputs | bore-interactive-inputs |
|---------|-------------------|------------------------|
| Tunnel Service | ngrok (requires signup) | bore (self-hostable) |
| Implementation | TypeScript | Python |
| File Uploads | ✅ | ✅ |
| Slack Integration | ✅ | ✅ |
| Discord Integration | ✅ | ✅ |
| Self-hosting | ❌ | ✅ |
| Maintenance | Complex | Simpler (Python) |

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Inspired by [boasiHQ/interactive-inputs](https://github.com/boasiHQ/interactive-inputs)
- Uses [ekzhang/bore](https://github.com/ekzhang/bore) for tunneling
