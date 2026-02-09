# Git Workflow & Security Guide

## 🔒 Security First - ALWAYS Verify Before Committing

### Pre-Commit Security Checklist

```bash
# 1. Check what files will be committed
git status

# 2. Verify NO sensitive files are staged
git diff --cached --name-only | grep -E "\.env$|credentials|\.key$|\.db$"

# 3. If any sensitive files appear, unstage them
git reset HEAD <sensitive-file>
```

---

## ✅ Safe Files to Commit

### Always Safe:
- ✅ `.env.example` (template only)
- ✅ `*.md` (documentation)
- ✅ `*.py` (Python code - no credentials)
- ✅ `.gitignore`
- ✅ `requirements.txt`
- ✅ `README.md`

### Check Before Committing:
- ⚠️ Config files (ensure no credentials)
- ⚠️ Test scripts (ensure no hardcoded keys)
- ⚠️ Notebooks (may contain output with sensitive data)

---

## ❌ NEVER Commit These Files

### Absolutely Forbidden:
- ❌ `.env` (contains real credentials)
- ❌ `*.db`, `*.sqlite` (database with trading data)
- ❌ `*.key`, `*.pem` (encryption keys)
- ❌ `config/*credentials*` (credential files)
- ❌ `logs/` (may contain sensitive data)
- ❌ `backups/` (database backups)
- ❌ `keys/` (encryption keys)

**These are already in `.gitignore` - but always verify!**

---

## 📝 Standard Workflow

### 1. Make Changes
```bash
# Edit files
nano src/risk_management/risk_calculator.py
```

### 2. Check Status (Security Check)
```bash
# ALWAYS check before committing
git status

# Verify no .env file appears
# Verify no .db files appear
# Verify no credential files appear
```

### 3. Stage Safe Files Only
```bash
# Option A: Stage specific files (RECOMMENDED)
git add src/risk_management/risk_calculator.py
git add docs/RISK_MANAGEMENT.md

# Option B: Stage all (ONLY if status looks safe)
git add .

# NEVER use: git add -f .env  (force add - dangerous!)
```

### 4. Review Changes
```bash
# See what will be committed
git diff --cached

# List files to be committed
git diff --cached --name-only
```

### 5. Commit with Descriptive Message
```bash
git commit -m "feat: Add risk calculator with 1% rule enforcement

- Implement ATR-based stop loss calculation
- Add position sizing with 1% risk rule
- Add tests for risk calculator
- Update documentation"
```

### 6. Push to GitHub
```bash
git push origin master
```

---

## 🚨 Emergency: Accidentally Committed Sensitive File

### If You Haven't Pushed Yet:

```bash
# Remove file from last commit (keep local changes)
git reset --soft HEAD~1
git reset HEAD <sensitive-file>

# Commit again without sensitive file
git add <safe-files>
git commit -m "Your message"
```

### If You Already Pushed (CRITICAL):

```bash
# 1. Remove file from git history (dangerous!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push (overwrites remote)
git push origin --force --all

# 3. IMMEDIATELY rotate all exposed credentials:
# - Generate new API keys
# - Change passwords
# - Regenerate encryption keys
```

**Better:** Contact GitHub support to delete repository and recreate.

---

## 📊 Useful Git Commands

### Check Repository Status
```bash
# See what's changed
git status

# See what's in .gitignore
cat .gitignore

# List all tracked files
git ls-files

# Search for specific files in repo
git ls-files | grep -E "\.env$|credentials"
```

### View History
```bash
# See recent commits
git log --oneline -10

# See files changed in last commit
git show --name-only

# See all commits for a file
git log --follow -- path/to/file
```

### Branch Management
```bash
# Create new branch for feature
git checkout -b feature/risk-management

# Switch back to master
git checkout master

# Merge feature branch
git merge feature/risk-management

# Delete branch after merge
git branch -d feature/risk-management
```

---

## 🎯 Commit Message Best Practices

### Format:
```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `security`: Security improvements

### Examples:

**Good Commit Messages:**
```bash
git commit -m "feat: Implement position sizer with 1% risk rule"

git commit -m "fix: Correct stop loss calculation for short positions"

git commit -m "docs: Add risk management examples to README"

git commit -m "security: Add input validation for order parameters"
```

**Bad Commit Messages:**
```bash
git commit -m "update"  # Too vague
git commit -m "fixed stuff"  # What stuff?
git commit -m "changes"  # What changed?
```

---

## 🔐 Security Verification Script

Create this script to verify before commits:

```bash
#!/bin/bash
# verify_commit.sh - Run before committing

echo "🔍 Security Verification..."

# Check for sensitive files
SENSITIVE_FILES=$(git diff --cached --name-only | grep -E "\.env$|credentials|\.key$|\.db$|\.pem$")

if [ -n "$SENSITIVE_FILES" ]; then
    echo "❌ SENSITIVE FILES DETECTED:"
    echo "$SENSITIVE_FILES"
    echo ""
    echo "Remove these files from staging:"
    echo "$SENSITIVE_FILES" | while read file; do
        echo "  git reset HEAD $file"
    done
    exit 1
fi

# Check for potential credentials in code
POTENTIAL_CREDS=$(git diff --cached | grep -iE "password\s*=|api_key\s*=|secret\s*=" | grep -v "\.env\.example")

if [ -n "$POTENTIAL_CREDS" ]; then
    echo "⚠️  WARNING: Potential credentials in code:"
    echo "$POTENTIAL_CREDS"
    echo ""
    echo "Verify these are not real credentials!"
    read -p "Continue anyway? (y/N): " confirm
    if [ "$confirm" != "y" ]; then
        exit 1
    fi
fi

echo "✅ Security check passed!"
exit 0
```

**Usage:**
```bash
chmod +x verify_commit.sh
./verify_commit.sh && git commit -m "Your message"
```

---

## 📋 Daily Git Workflow

### Morning (Start Work):
```bash
# Pull latest changes
git pull origin master

# Create feature branch
git checkout -b feature/portfolio-risk-manager

# Start coding...
```

### During Work:
```bash
# Save progress frequently
git add src/risk_management/
git commit -m "wip: Portfolio risk manager implementation"

# Push to backup
git push origin feature/portfolio-risk-manager
```

### End of Day:
```bash
# Security check
git status

# Commit final changes
git add .
git commit -m "feat: Complete portfolio risk manager

- Implement max positions limit (3)
- Add daily loss tracking (3%)
- Add correlation checking
- Add comprehensive tests"

# Push to GitHub
git push origin feature/portfolio-risk-manager
```

### When Feature Complete:
```bash
# Switch to master
git checkout master

# Merge feature
git merge feature/portfolio-risk-manager

# Push to GitHub
git push origin master

# Delete feature branch
git branch -d feature/portfolio-risk-manager
git push origin --delete feature/portfolio-risk-manager
```

---

## 🎓 Git Best Practices for Trading System

### 1. Commit Often
- Small, focused commits
- Easier to review
- Easier to rollback if needed

### 2. Never Commit Sensitive Data
- Always check `git status` first
- Use `.gitignore` properly
- Keep credentials in `.env` only

### 3. Write Good Commit Messages
- Explain WHY, not just WHAT
- Reference issue numbers
- Be descriptive

### 4. Use Branches for Features
- `master` - stable, tested code
- `feature/risk-calculator` - new features
- `fix/stop-loss-bug` - bug fixes

### 5. Test Before Committing
- Run tests: `pytest`
- Check linting: `flake8`
- Verify security: `./verify_commit.sh`

---

## 🚀 Collaboration Workflow

### Pull Requests:
```bash
# Create feature branch
git checkout -b feature/trailing-stop-loss

# Make changes and commit
git add .
git commit -m "feat: Add trailing stop loss"

# Push to GitHub
git push origin feature/trailing-stop-loss

# Create Pull Request on GitHub
# Get review from team
# Merge when approved
```

### Code Review Checklist:
- [ ] No sensitive data in commits
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] Commit messages are clear

---

## 📖 Additional Resources

- **Git Basics**: https://git-scm.com/book/en/v2
- **GitHub Guides**: https://guides.github.com/
- **Git Security**: https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Git_Cheat_Sheet.md

---

## ⚠️ Remember

**The #1 Rule**: Never commit credentials!

If you're unsure whether a file contains sensitive data:
1. Review the file manually
2. Ask: "Would I be comfortable with this being public?"
3. When in doubt, don't commit it

**Your trading system's security depends on it!**
