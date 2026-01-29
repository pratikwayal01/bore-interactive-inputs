# Why Bore Interactive Inputs?

## Overview

This GitHub Action provides the same functionality as [interactive-inputs](https://github.com/boasiHQ/interactive-inputs) but with important advantages, especially if you prefer Python and want to self-host your tunneling infrastructure.

## Key Advantages

### 1. **Self-Hostable Tunnel (Bore)**

**interactive-inputs** uses ngrok, which:
- Requires signup and authentication token
- Has usage limits on free tier
- Requires trusting a third-party service
- Cannot be self-hosted

**bore-interactive-inputs** uses bore, which:
- ✅ Can be self-hosted on your own infrastructure
- ✅ No signup required for public server (bore.pub)
- ✅ Open source and transparent
- ✅ Simple Rust binary - easy to deploy
- ✅ Optional authentication with secrets
- ✅ Full control over your data

### 2. **Python Implementation**

**interactive-inputs** is written in TypeScript/JavaScript:
- Requires Node.js knowledge
- More complex build process
- Harder to debug in GitHub Actions environment

**bore-interactive-inputs** is written in Python:
- ✅ More readable and maintainable
- ✅ Easier to extend and modify
- ✅ Better for data processing and file handling
- ✅ Simpler dependency management
- ✅ More accessible for DevOps engineers

### 3. **Simplified Architecture**

```
interactive-inputs:
TypeScript → Compile → Bundle → Distribute → Run

bore-interactive-inputs:
Python → Run directly (no build step needed)
```

### 4. **Better for Security-Conscious Organizations**

If you work in a regulated industry or have strict security requirements:

- **Self-hosted bore** means your workflow data never touches third-party servers
- **Open source tunnel** allows security audits
- **No external dependencies** for the tunnel service
- **Optional authentication** for added security

## Feature Comparison

| Feature | interactive-inputs | bore-interactive-inputs |
|---------|-------------------|------------------------|
| Text inputs | ✅ | ✅ |
| File uploads | ✅ | ✅ |
| Multi-select | ✅ | ✅ |
| Slack notifications | ✅ | ✅ |
| Discord notifications | ✅ | ✅ |
| Self-hostable tunnel | ❌ | ✅ |
| No external signup | ❌ | ✅ |
| Python-based | ❌ | ✅ |
| Easy to modify | ⚠️ | ✅ |
| TypeScript-based | ✅ | ❌ |

## When to Use Each

### Use **interactive-inputs** if:
- You're already using ngrok
- You prefer TypeScript/JavaScript
- You don't need self-hosting
- You're comfortable with ngrok's terms and limits

### Use **bore-interactive-inputs** if:
- You want to self-host your tunnel
- You prefer Python
- You have strict security requirements
- You want simpler code to maintain
- You want to avoid external service dependencies
- You're working in a regulated environment

## Self-Hosting Example

With **bore-interactive-inputs**, you can run your own tunnel server:

```bash
# On your server
bore server --bind-addr 0.0.0.0 --secret $BORE_SECRET

# In your workflow
- uses: yourusername/bore-interactive-inputs@v1
  with:
    bore-server: 'your-server.com'
    bore-secret: ${{ secrets.BORE_SECRET }}
```

This is **impossible** with interactive-inputs because ngrok cannot be self-hosted.

## Technical Details

### Bore Tunnel Advantages

1. **Simple Protocol**: Bore uses a simple TCP proxy protocol
2. **Lightweight**: Rust binary with minimal overhead
3. **Fast**: Direct TCP tunneling without HTTP overhead
4. **Secure**: Optional secret authentication
5. **Reliable**: Simple architecture means fewer failure points

### Python Advantages for This Use Case

1. **Flask**: Simple, well-tested web framework
2. **File Handling**: Python excels at file I/O operations
3. **YAML Parsing**: Native YAML support
4. **Requests**: Simple HTTP client for notifications
5. **Subprocess**: Easy process management for bore

## Migration from interactive-inputs

If you're currently using interactive-inputs, migration is straightforward:

```yaml
# Before (interactive-inputs)
- uses: boasiHQ/interactive-inputs@v2
  with:
    ngrok-authtoken: ${{ secrets.NGROK_AUTHTOKEN }}
    interactive: |
      fields:
        - label: environment
          properties:
            type: select
            choices: [dev, prod]

# After (bore-interactive-inputs)
- uses: yourusername/bore-interactive-inputs@v1
  with:
    bore-server: 'bore.pub'  # or your server
    interactive: |
      fields:
        - label: environment
          properties:
            type: select
            choices: [dev, prod]
```

**Changes:**
1. Replace `ngrok-authtoken` with `bore-server`
2. Optionally add `bore-secret` if using authentication
3. Everything else stays the same!

## Cost Comparison

### ngrok (used by interactive-inputs)

- **Free tier**: Limited tunnels, sessions, bandwidth
- **Pro**: $10-20/month per user
- **Enterprise**: Custom pricing

### bore (used by bore-interactive-inputs)

- **Public bore.pub**: Free, no limits
- **Self-hosted**: Only server costs (~$5-10/month for small VPS)
- **No per-user fees**
- **No bandwidth limits** (if self-hosted)

## Real-World Scenarios

### Scenario 1: Financial Services Company

**Requirement**: All data must stay within company infrastructure

**Solution**: Self-host bore server on internal infrastructure
```yaml
with:
  bore-server: 'tunnel.internal.company.com'
  bore-secret: ${{ secrets.INTERNAL_BORE_SECRET }}
```

### Scenario 2: Open Source Project

**Requirement**: No paid services, easy contributor setup

**Solution**: Use public bore.pub server
```yaml
with:
  bore-server: 'bore.pub'
```
No signup required for contributors!

### Scenario 3: DevOps Team

**Requirement**: Easy to maintain and extend

**Solution**: Python codebase is easier for DevOps engineers
```python
# Easy to add custom field validation
def validate_field(field, value):
    if field['type'] == 'email':
        return validate_email(value)
    return True
```

## Conclusion

Both actions solve the same problem, but **bore-interactive-inputs** is better if:

1. ✅ You want self-hosting capabilities
2. ✅ You prefer Python over TypeScript
3. ✅ You have security/compliance requirements
4. ✅ You want to avoid external service dependencies
5. ✅ You want simpler, more maintainable code

Choose the tool that best fits your team's needs and constraints!

## Questions?

Create an issue in the repository and we'll help you decide if bore-interactive-inputs is right for your use case.
