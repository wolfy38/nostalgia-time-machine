# Contributing to The Nostalgia Time Machine 🚀

Thank you for your interest in contributing to The Nostalgia Time Machine! This document provides guidelines and information for contributors.

## How Can I Contribute? 🤝

### Reporting Bugs

- Use the GitHub issue tracker
- Provide detailed information about the bug
- Include steps to reproduce the issue
- Mention your operating system and browser

### Suggesting Enhancements

- Open a feature request issue
- Describe the enhancement clearly
- Explain why this feature would be useful
- Provide examples if possible

### Code Contributions

- Fork the repository
- Create a feature branch
- Make your changes
- Test thoroughly
- Submit a pull request

## Development Setup 🛠️

### Prerequisites

- Python 3.7+
- MongoDB
- Node.js (for package management)

### Local Development

1. Fork and clone the repository
2. Set up virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Set up MongoDB and start the service
5. Create a `.env` file with your configuration
6. Run the application:
   ```bash
   python app.py
   ```

## Code Style Guidelines 📝

### Python

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions small and focused

### JavaScript

- Use ES6+ features
- Follow consistent naming conventions
- Add comments for complex logic
- Use meaningful variable names

### HTML/CSS

- Use semantic HTML elements
- Follow BEM methodology for CSS
- Keep CSS organized and commented
- Ensure responsive design

## Testing 🧪

### Before Submitting

- Test your changes thoroughly
- Ensure all existing functionality works
- Test on different browsers and devices
- Check for any console errors

### Writing Tests

- Add unit tests for new functionality
- Test edge cases and error conditions
- Ensure good test coverage

## Pull Request Process 📋

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```
4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** with:
   - Clear description of changes
   - Screenshots if UI changes
   - Reference to related issues

### Commit Message Format

Use conventional commit format:

- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for improvements
- `Remove:` for deletions
- `Refactor:` for code refactoring

## Code Review Process 👀

- All PRs will be reviewed by maintainers
- Address feedback and make requested changes
- Ensure CI/CD checks pass
- Maintainers will merge after approval

## Getting Help 💬

- Open an issue for questions
- Join our community discussions
- Check existing documentation
- Review previous issues and PRs

## License 📄

By contributing, you agree that your contributions will be licensed under the ISC License.

## Recognition 🏆

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to The Nostalgia Time Machine! 🌟
