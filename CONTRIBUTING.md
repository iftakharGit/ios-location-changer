# Contributing to iOS Location Changer

First off, thank you for considering contributing to iOS Location Changer! It's people like you that make open-source software such a great community.

## 🛠️ Development Setup

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/iftakharGit/ios-location-changer.git
   cd ios-location-changer
   ```
3. **Set up your Python virtual environment** (Requires Python 3.14+):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install flake8 pytest pytest-asyncio httpx
   ```

## 🧪 Code Standards & Testing

This project enforces strict code quality and accessibility standards. We use **GitHub Actions** to automatically reject Pull Requests that fail tests or contain syntax errors.

Before submitting a Pull Request, you **must** verify your code locally:

1. **Run the Linter (Flake8):**
   ```bash
   flake8 backend/ app.py tests/
   ```
   *Ensure there are no syntax errors, undefined variables, or major formatting issues.*

2. **Run the Test Suite (Pytest):**
   ```bash
   pytest tests/
   ```
   *All tests must pass. If you are adding a new feature to the `DeviceManager` or `API`, please include a corresponding test in the `tests/` folder.*

## 🚀 Pull Request Process

1. Create a new branch for your feature (`git checkout -b feature/amazing-feature`).
2. Make your changes and commit them using clear, descriptive commit messages.
3. Push your branch to your fork (`git push origin feature/amazing-feature`).
4. Open a **Pull Request** against our `main` branch.
5. Wait for the automated CI/CD pipeline to turn green (✅). If it fails, please review the GitHub Actions log, fix the issue, and push your updates.

We will review your Pull Request as soon as possible!
