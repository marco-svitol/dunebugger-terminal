# Dunebugger Terminal

[![Semantic Release](https://github.com/marco-svitol/dunebugger-terminal/actions/workflows/semantic-release.yml/badge.svg)](https://github.com/marco-svitol/dunebugger-terminal/actions/workflows/semantic-release.yml)
[![Version](https://img.shields.io/github/v/release/marco-svitol/dunebugger-terminal?include_prereleases)](https://github.com/marco-svitol/dunebugger-terminal/releases)

A terminal interface component for the Dunebugger hardware debugging system. This component provides an interactive command-line interface to communicate with and control hardware devices via a distributed messaging system.

## Overview

Dunebugger Terminal is designed to provide remote terminal access to hardware debugging operations, particularly GPIO control and monitoring. It connects to a NATS message broker to communicate with other system components, offering a clean command-line interface for hardware interaction.

### Key Features

- **Interactive Terminal Interface**: Command-line interface with readline support and history
- **Distributed Messaging**: NATS-based communication with other system components
- **GPIO Management**: View GPIO status, configuration, and control hardware switches
- **Automatic Reconnection**: Robust connection handling with automatic recovery
- **Version Management**: Semantic versioning with production/development detection
- **Raspberry Pi Detection**: Platform-aware functionality
- **Colored Output**: Enhanced user experience with color-coded messages
- **Asynchronous Architecture**: Non-blocking operations for responsive interaction

## Architecture

The terminal acts as a client in a distributed system:

```
┌─────────────────┐    NATS     ┌─────────────────┐
│ Dunebugger      │◄───────────►│ Dunebugger Core │
│ Terminal        │   Messages  │ (GPIO Control)  │
└─────────────────┘             └─────────────────┘
        │
        ▼
┌─────────────────┐
│ User Interface  │
│ (CLI/Terminal)  │
└─────────────────┘
```

### Components

- **Terminal Interpreter**: Handles user input and command processing
- **NATS Communication**: Message queue interface for distributed communication
- **Configuration Manager**: Handles settings and environment detection
- **Version System**: Development and production version management
- **Logging System**: Structured logging with colored output

## Installation

### Prerequisites

- Python 3.8+
- NATS server (for messaging)
- Optional: Raspberry Pi for GPIO functionality

### From Release (Production)

1. Download the latest release artifact:
```bash
# Download from GitHub Releases
wget https://github.com/marco-svitol/dunebugger-terminal/releases/download/v1.0.0/dunebugger-terminal-1.0.0.tar.gz
wget https://github.com/marco-svitol/dunebugger-terminal/releases/download/v1.0.0/dunebugger-terminal-1.0.0.tar.gz.sha256

# Verify integrity
sha256sum -c dunebugger-terminal-1.0.0.tar.gz.sha256

# Extract
tar xzf dunebugger-terminal-1.0.0.tar.gz -C /opt/dunebugger-terminal/
```

2. Install dependencies:
```bash
cd /opt/dunebugger-terminal
pip install -r requirements.txt
```

### From Source (Development)

1. Clone the repository:
```bash
git clone https://github.com/marco-svitol/dunebugger-terminal.git
cd dunebugger-terminal
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Configuration File

Edit [app/config/dunebugger.conf](app/config/dunebugger.conf):

```ini
[General]

[MessageQueue]
mQueueServers = nats://nats-server:4222
mQueueClientID = terminal
mQueueSubjectRoot = dunebugger

[Log]
dunebuggerLogLevel = DEBUG
```

### Environment Variables

The application can be configured via:
- Configuration files
- Environment variables (via `dotenv`)
- Runtime detection (Raspberry Pi, etc.)

## Usage

### Starting the Terminal

```bash
python3 app/main.py
```

The terminal will:
1. Display version information
2. Connect to the NATS message broker
3. Request available commands from the core system
4. Present an interactive command prompt

### Available Commands

Once connected, the terminal provides access to system commands:

- **Hardware Control**: GPIO manipulation, device control
- **System Status**: View GPIO states, configuration, system information
- **Built-in Commands**:
  - `h` or `?`: Show help
  - `s`: Show GPIO status
  - `t`: Show configuration
  - `q`, `quit`, `exit`: Exit the program

### Example Session

```
Dunebugger terminal version: 1.0.0-beta.1-release+90b6f45
INFO - 13/01/2026 10:30:45 : Starting NATS connection manager (non-blocking)
INFO - 13/01/2026 10:30:45 : Connected to NATS messaging server: nats://nats-server:4222
INFO - 13/01/2026 10:30:45 : Listening for messages on queue dunebugger.terminal.

Enter command: help
I am not a Raspberry. You can ask me to:
    gpio_on: Turn on a GPIO pin
    gpio_off: Turn off a GPIO pin
    gpio_status: Show GPIO status
    h, ?: show this help
    s: show GPIO status
    t: show dunebugger configuration
    q, quit, exit: exit the program

Enter command: s
Pin   Logic                Label                Mode     State    Switch  
------------------------------------------------------------------------
18    RELAY_1             Main Power           OUTPUT   HIGH     ON      
19    RELAY_2             Debug Enable         OUTPUT   LOW      OFF     

Enter command: exit
Cleaning up resources...
Cleanup completed.
```

## Message Protocol

### Message Format

All messages use JSON format via NATS subjects:

```
Subject: {subject_root}.{client_id}.{command}
Payload: {
  "body": <command_data>,
  "subject": "<command_type>",
  "source": "<sender_id>"
}
```

### Supported Message Types

- `terminal_command`: Send commands to core system
- `get_version`: Request version information
- `commands_list`: Retrieve available commands
- `show_gpio_status`: Request GPIO status
- `show_configuration`: Request system configuration

## Development

### Project Structure

```
dunebugger-terminal/
├── app/
│   ├── main.py                 # Application entry point
│   ├── terminal_interpreter.py # User interface handler
│   ├── mqueue.py              # NATS communication
│   ├── mqueue_handler.py      # Message processing
│   ├── class_factory.py       # Dependency injection
│   ├── version.py             # Version management
│   ├── utils.py               # Utility functions
│   ├── dunebugger_settings.py # Configuration management
│   ├── dunebugger_logging.py  # Logging setup
│   └── config/
│       ├── dunebugger.conf    # Main configuration
│       └── dunebuggerlogging.conf # Logging configuration
├── requirements.txt           # Python dependencies
├── generate_version.sh       # Version file generator
├── CHANGELOG.md             # Release history
├── VERSIONING.md           # Versioning documentation
└── .github/workflows/      # CI/CD automation
```

### Running in Development

1. Start NATS server:
```bash
# Using Docker
docker run -p 4222:4222 -p 8222:8222 nats:latest

# Or install locally
nats-server
```

2. Run the application:
```bash
cd app
python3 main.py
```

### Code Quality

The project uses:
- **Black**: Code formatting (500 char line length)
- **Flake8**: Linting
- **Pre-commit**: Automated code quality checks
- **Semantic Release**: Automated versioning

Setup pre-commit hooks:
```bash
pre-commit install
```

## Versioning

This project uses [Semantic Versioning](https://semver.org/) with automated releases:

- **Production releases**: `main` branch → `1.2.3`
- **Beta releases**: `develop` branch → `1.3.0-beta.1`
- **Development builds**: Detected via git → `1.2.3-dev5+abc1234`

### Release Process

1. Use [Conventional Commits](https://conventionalcommits.org/):
   ```bash
   git commit -m "feat: add new terminal command"
   git commit -m "fix: resolve connection timeout issue"
   git commit -m "feat!: breaking change in API"
   ```

2. Push to appropriate branch:
   ```bash
   git push origin develop  # For beta releases
   git push origin main     # For production releases
   ```

3. GitHub Actions automatically:
   - Determines version bump
   - Generates changelog
   - Creates release artifacts
   - Publishes to GitHub Releases

See [VERSIONING.md](VERSIONING.md) for complete details.

## API Integration

### Version Information

Query version programmatically:

```python
from app.version import get_version_info

version = get_version_info()
print(f"Version: {version['full_version']}")
# Output: Version: 1.0.0-beta.1+90b6f45
```

### Message Queue Integration

Send version requests via NATS:

```python
# Send to terminal component
subject = "dunebugger.terminal.get_version"
# Receive response on "dunebugger.{your_client}.version_info"
```

## Deployment

### Production Deployment

1. Download verified release artifact
2. Extract to target directory
3. Install dependencies from `requirements.txt`
4. Configure NATS connection in `app/config/dunebugger.conf`
5. Run with `python3 app/main.py`

### Docker Deployment

Example Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY VERSION .

CMD ["python3", "app/main.py"]
```

### Systemd Service

Create `/etc/systemd/system/dunebugger-terminal.service`:

```ini
[Unit]
Description=Dunebugger Terminal Interface
After=network.target

[Service]
Type=simple
User=dunebugger
WorkingDirectory=/opt/dunebugger-terminal
ExecStart=/usr/bin/python3 app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Monitoring and Logging

### Log Levels

- `DEBUG`: Detailed connection and message information
- `INFO`: General operational information
- `WARNING`: Non-critical issues
- `ERROR`: Error conditions
- `CRITICAL`: Critical system failures

### Log Output

Logs are output to:
- Console (colored, formatted)
- File: `dunebugger.log`
- Optional USB logging (production)

### Monitoring Connection Status

The application provides connection status:
- NATS connection state
- Automatic reconnection attempts
- Message queue health

## Troubleshooting

### Common Issues

1. **Cannot connect to NATS**:
   - Verify NATS server is running
   - Check `mQueueServers` configuration
   - Review network connectivity

2. **No commands available**:
   - Ensure core system is running
   - Verify message subject configuration matches between components

3. **GPIO not working**:
   - Confirm running on Raspberry Pi
   - Check GPIO permissions
   - Verify hardware connections

### Debug Mode

Enable debug logging:

```ini
# In app/config/dunebugger.conf
[Log]
dunebuggerLogLevel = DEBUG
```

### Connection Debugging

Monitor NATS traffic:
```bash
# Install NATS CLI tools
nats sub "dunebugger.>"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes following code style guidelines
4. Add tests if applicable
5. Use conventional commits: `git commit -m "feat: add new feature"`
6. Push and create a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/marco-svitol/dunebugger-terminal.git
cd dunebugger-terminal

# Install development dependencies
pip install -r requirements.txt
pre-commit install

# Make changes and test
python3 app/main.py
```

## License

This project is part of the Dunebugger hardware debugging system.

## Support

For issues and questions:
- Create an issue on GitHub
- Review existing documentation
- Check the troubleshooting section

---

**Dunebugger Terminal** - Interactive hardware debugging interface