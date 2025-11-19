# Contributing to Code Smell Detective 🕵️

Welcome, fellow detective! You've decided to join the Code Smell Detective agency and help us solve the case of code quality. We're thrilled to have you on the team!

## The Investigation Process

Every good detective follows a systematic approach. Here's how we handle contributions to the Code Smell Detective repository:

### Step 1: Clone the Repository (Gathering Evidence)

First, you'll need to obtain a copy of the case files on your local machine:

```bash
git clone https://github.com/code-smell-detective/code-smell-detective.git
cd code-smell-detective
```

### Step 2: Set Up Your Investigation Environment

Before you start your investigation, make sure you have all the necessary tools:

```bash
# Install the package in development mode
pip install -e ".[dev]"

# Verify everything is working
pytest
```

### Step 3: Create a New Branch (Your Investigation Branch)

Never work directly on the `main` branch! Each new feature, bug fix, or improvement should be investigated on its own branch. Think of it as opening a new case file.

```bash
# Make sure you're on the main branch and it's up to date
git checkout main
git pull origin main

# Create and switch to your new investigation branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix-name
# or
git checkout -b docs/your-documentation-update
```

**Branch Naming Convention:**
- `feature/` - for new features or enhancements
- `fix/` - for bug fixes
- `docs/` - for documentation updates
- `refactor/` - for code refactoring
- `test/` - for adding or updating tests

### Step 4: Conduct Your Investigation

Now it's time to do your detective work! Make your changes, write your code, and gather your evidence (tests). Remember:

- **Write clean code** - We're detecting code smells, so let's not introduce any ourselves!
- **Add tests** - Every good detective documents their findings. Tests are our evidence.
- **Follow the existing code style** - Consistency is key in any investigation.
- **Update documentation** - If you're adding a new feature, make sure the case files are updated.

### Step 5: Commit Your Findings

Once you've completed your investigation, it's time to document your findings with clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add new code smell detector for magic numbers"
# or
git commit -m "fix: resolve issue with duplicate code detection in nested functions"
```

**Commit Message Guidelines:**
- Use conventional commit format: `type: description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Keep descriptions clear and concise
- Reference issue numbers if applicable: `feat: add feature (#123)`

### Step 6: Push Your Branch and Create a Pull Request

Submit your findings for review by pushing your branch and creating a pull request:

```bash
git push origin feature/your-feature-name
```

Then, navigate to the repository on GitHub and create a Pull Request. Make sure to:

- **Provide a clear title** - What case are you solving?
- **Write a detailed description** - Explain what you investigated, what you found, and how you solved it
- **Reference any related issues** - Link to issues if your PR addresses them
- **Include screenshots or examples** - If applicable, show the evidence

### Step 7: The Review Process (Case Review)

Once you've submitted your Pull Request, the case goes under review. Here's what happens:

1. **Automated Checks** - Our automated systems will run tests and linting to ensure code quality
2. **Code Review** - A senior detective (maintainer) will review your investigation
3. **Feedback** - You may receive feedback or requests for changes
4. **Approval or Denial** - The maintainer will either:
   - ✅ **Approve** - Your investigation is solid, and the PR will be merged
   - ❌ **Deny** - The investigation needs more work, with clear reasons provided

**If your PR is denied:**
- Don't worry! Every detective learns from feedback
- Review the comments carefully
- Make the requested changes
- Push updates to the same branch (the PR will update automatically)
- Ask questions if anything is unclear

## Investigation Guidelines

### Code Quality Standards

- **No code smells!** - Run the detector on your own code before submitting
- **Follow PEP 8** - Python style guide is our standard operating procedure
- **Type hints** - Where possible, include type hints for better code clarity
- **Docstrings** - Document your functions and classes

### Testing Requirements

- **Write tests** - New features should include tests
- **Maintain coverage** - Don't decrease test coverage
- **Test edge cases** - Good detectives think about all scenarios

### What to Investigate

We welcome contributions in many areas:

- 🐛 **Bug Fixes** - Help us catch the bugs
- ✨ **New Features** - Add new code smell detectors or capabilities
- 📚 **Documentation** - Improve our case files and guides
- 🧪 **Tests** - Strengthen our test coverage
- 🎨 **Code Quality** - Refactor and improve existing code
- 🚀 **Performance** - Optimize our detection algorithms

## Getting Help

Stuck on a case? Need help with your investigation?

- **Open an Issue** - Report bugs or suggest features
- **Ask Questions** - Don't hesitate to ask for clarification
- **Check Existing Issues** - Someone might have already reported the same case

## Code of Conduct

As detectives, we maintain professionalism and respect:

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the project's coding standards

## Thank You! 🎉

Thank you for joining the Code Smell Detective agency! Your contributions help us solve the mystery of code quality, one smell at a time. Every contribution, no matter how small, makes a difference.

Happy investigating! 🕵️‍♂️🕵️‍♀️

