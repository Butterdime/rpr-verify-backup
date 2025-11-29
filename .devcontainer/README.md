# Development Container for RPR CIS Dashboard

This project includes a devcontainer configuration for GitHub Codespaces and VS Code Dev Containers, enabling instant cloud-based development with all required tools preinstalled.

## Features

- **Python 3.11** with pip for dependency management
- **Node.js LTS** for Firebase CLI support
- **Firebase CLI** for deployment and emulator workflows
- **VS Code Extensions**: Python, Pylance, Debugpy, and Firebase tools
- **Port Forwarding**: Port 5000 (Flask app) is automatically forwarded

## Getting Started

### Using GitHub Codespaces

1. Click the **Code** button on the repository page
2. Select the **Codespaces** tab
3. Click **Create codespace on main** (or your target branch)
4. Wait for the container to build and dependencies to install

### Using VS Code Dev Containers

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the repository folder in VS Code
3. Click **Reopen in Container** when prompted, or use the Command Palette (`Ctrl+Shift+P`) and select **Dev Containers: Reopen in Container**

## Running the Application

Once the container is ready, start the Flask application from the project root:

```bash
python ui/app.py
```

The app will be available at `http://localhost:5000` (automatically forwarded).

## Running Tests

```bash
python -m unittest discover tests/
```

## Firebase Setup

The Firebase CLI is preinstalled. To authenticate and deploy:

```bash
firebase login
firebase init
firebase deploy
```

## Notes

- All Python dependencies from `requirements.txt` are automatically installed via `postCreateCommand`
- Tesseract OCR may need additional setup for OCR functionality (see main README)
