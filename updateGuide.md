# Production Server Update Guide

## Quick Reference

### Push from Local Computer → GitHub
```bash
git add .
git commit -m "Your descriptive message"
git push origin main
```

### Pull from GitHub → Production Server
```bash
git stash  # Save local changes
git pull origin main
pip install -r requirements.txt  # If dependencies changed
pkill -9 -f uvicorn && nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &  # Restart app
```

---

## The Complete Git Pull Workflow

### Step-by-Step: Updating Production Server

#### Step 1: Save any local server changes
```bash
git stash push -m "Server local changes"
```

This temporarily saves any uncommitted changes you made on the server.

#### Step 2: Pull latest changes from GitHub
```bash
git pull origin main
```

This downloads and applies all changes from your GitHub repository.

#### Step 3: Update dependencies (if requirements.txt changed)
```bash
source venv/bin/activate
pip install -r requirements.txt
```

Only needed if you see `requirements.txt` in the changed files.

#### Step 4: Update .env file if needed
```bash
# Check what new variables were added
cat .env.example

# Edit your .env file to add any new variables
nano .env
```

Compare `.env.example` with your `.env` and add any missing variables.

#### Step 5: Restart the application
```bash
pkill -9 -f "uvicorn.*main:app"
nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &
```

Stops the old version and starts the new one.

#### Step 6: Verify it's working
```bash
curl http://localhost:8000/health
curl https://app.quz.ma/verbatim-ai/health
```

Both should return: `{"status":"healthy","openrouter_configured":true}`

---

## The Complete Git Push Workflow

### Step-by-Step: Pushing Changes from Local Computer

#### Step 1: Check what changed
```bash
git status
```

Shows:
- **Modified files** (files you changed)
- **Untracked files** (new files not in git yet)
- **Deleted files**

#### Step 2: Review your changes (optional but recommended)
```bash
# See what you changed in specific files
git diff filename.txt

# Or see all changes
git diff
```

#### Step 3: Stage files (prepare them for commit)

**Option A: Add specific files**
```bash
git add file1.txt file2.py file3.js
```

**Option B: Add all changed files**
```bash
git add .
```

**Option C: Add only certain types**
```bash
git add *.py          # All Python files
git add src/          # Everything in src folder
```

#### Step 4: Commit with a message
```bash
git commit -m "Your descriptive message here"
```

**Good commit messages:**
- ✅ "Fix timeout issue in AI formatting"
- ✅ "Add user authentication feature"
- ✅ "Update README with deployment instructions"

**Bad commit messages:**
- ❌ "update"
- ❌ "fixes"
- ❌ "changes"

#### Step 5: Push to GitHub
```bash
git push origin main
```

Or simply:
```bash
git push
```

---

## Complete Update Example (Production Server)

```bash
# Navigate to project directory
cd /var/www/app.quz.ma/verbatim-ai

# 1. Save any local server changes
git stash push -m "Server local changes"

# 2. Check what's new on GitHub (optional)
git fetch origin
git log HEAD..origin/main --oneline

# 3. Pull latest changes
git pull origin main

# 4. Update dependencies if needed
source venv/bin/activate
pip install -r requirements.txt

# 5. Check if .env needs updating
diff .env .env.example
# Add any missing variables to .env

# 6. Restart the application
pkill -9 -f "uvicorn.*main:app"
nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &

# 7. Verify it's working
sleep 3
curl http://localhost:8000/health
curl https://app.quz.ma/verbatim-ai/health

# 8. Check logs if there are issues
tail -f /tmp/verbatim-ai.log
```

---

## One-Liner Commands

### Quick Push (Local Computer)
```bash
git add . && git commit -m "Your message" && git push origin main
```

### Quick Pull and Restart (Production Server)
```bash
git stash && git pull origin main && pip install -r requirements.txt && pkill -9 -f uvicorn && nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &
```

---

## Common Scenarios

### Scenario 1: You changed existing files on local computer
```bash
# On local computer
git add .
git commit -m "Update feature X"
git push origin main

# On production server
git pull origin main
pkill -9 -f uvicorn && nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &
```

### Scenario 2: You added new files on local computer
```bash
# On local computer
git add .  # Adds new files
git commit -m "Add new module Y"
git push origin main

# On production server
git pull origin main
# Check if requirements.txt changed
pip install -r requirements.txt
pkill -9 -f uvicorn && nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &
```

### Scenario 3: You deleted files
```bash
# On local computer
git add .  # Stages deletions too
git commit -m "Remove old files"
git push origin main

# On production server
git pull origin main
pkill -9 -f uvicorn && nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &
```

### Scenario 4: Undo unstaged changes (be careful!)
```bash
git restore filename.txt  # Discard changes to one file
git restore .             # Discard ALL changes (DANGER!)
```

---

## Useful Git Commands

### Check if GitHub has updates
```bash
git fetch origin
git log HEAD..origin/main --oneline
```

### See what changed
```bash
git diff HEAD origin/main        # Before pulling - see what will change
git log -5 --oneline             # After pulling - see recent commits
git show <commit-hash>           # See details of specific commit
```

### Working with stash
```bash
git stash list                   # See all stashed changes
git stash pop                    # Apply and remove latest stash
git stash apply                  # Apply but keep stash
git stash drop                   # Delete latest stash
git stash clear                  # Delete all stashes
```

### Branch management
```bash
git branch                       # List local branches
git branch -a                    # List all branches (including remote)
git checkout -b feature-branch   # Create and switch to new branch
git checkout main                # Switch back to main
```

### View history
```bash
git log --oneline -10            # Last 10 commits
git log --graph --oneline        # Visual branch history
git log --author="YourName"      # Your commits only
git log --since="2 weeks ago"    # Recent commits
```

---

## Before You Pull - Checklist

- ✅ Do you have uncommitted changes? (`git status`)
- ✅ Should you stash them? (`git stash`)
- ✅ Check what's coming (`git fetch && git log HEAD..origin/main --oneline`)
- ✅ Are you on the right branch? (`git branch`)

---

## Before You Push - Checklist

- ✅ Did you test your changes?
- ✅ Is your commit message descriptive?
- ✅ Did you accidentally include sensitive files (.env, passwords)?
  ```bash
  # Check what you're committing
  git status
  git diff --cached
  ```
- ✅ Are you on the right branch? (`git branch`)

---

## Handling Conflicts

If you get merge conflicts during `git pull`:

```bash
# 1. Pull changes (conflict occurs)
git pull origin main

# 2. Git will tell you which files have conflicts
# Open each file and look for conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> origin/main

# 3. Edit the file to resolve conflicts

# 4. Stage the resolved files
git add resolved-file.py

# 5. Complete the merge
git commit -m "Resolve merge conflicts"

# 6. Restart the app
pkill -9 -f uvicorn && nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &
```

**Better approach - Avoid conflicts:**
```bash
git stash              # Save your changes
git pull origin main   # Pull cleanly
git stash pop          # Reapply your changes
# Resolve any conflicts
```

---

## Troubleshooting

### Problem: "Your branch is behind origin/main"
```bash
# Solution: Pull the latest changes
git pull origin main
```

### Problem: "Your branch is ahead of origin/main"
```bash
# Solution: You have local commits, push them
git push origin main
```

### Problem: "fatal: could not read Username"
```bash
# Solution: You need to authenticate
# Use SSH (already set up):
git remote -v
# Should show: git@github.com:DarkoKuzmanovic/verbatim-ai.git
```

### Problem: Application won't start after pull
```bash
# Check the logs
tail -f /tmp/verbatim-ai.log

# Common issues:
# 1. Missing dependencies
pip install -r requirements.txt

# 2. Missing .env variables
cat .env.example
nano .env

# 3. Port already in use
pkill -9 -f uvicorn
nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &

# 4. Permission issues
chmod +x start.sh
```

### Problem: Nginx shows 502 Bad Gateway
```bash
# Check if app is running
curl http://localhost:8000/health

# If not running, restart it
pkill -9 -f uvicorn
nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &

# Check nginx logs
tail -f /var/log/nginx/error.log
```

### Problem: Static files not loading
```bash
# Check nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Verify static files exist
ls -la static/
```

---

## Monitoring Your Application

### Check if app is running
```bash
ps aux | grep -E "[u]vicorn.*main:app"
```

### View application logs
```bash
tail -f /tmp/verbatim-ai.log
```

### View nginx logs
```bash
# Access logs
tail -f /var/log/nginx/app.quz.ma-access.log

# Error logs
tail -f /var/log/nginx/app.quz.ma-error.log
```

### Test endpoints
```bash
# Health check
curl http://localhost:8000/health

# Public health check
curl https://app.quz.ma/verbatim-ai/health

# Test transcript endpoint
curl -X POST http://localhost:8000/api/transcript \
  -H "Content-Type: application/json" \
  -d '{"youtube_url":"https://youtube.com/watch?v=dQw4w9WgXcQ"}' \
  | python3 -m json.tool | head -20
```

---

## Pro Tips

### Tip 1: Always check before pulling
```bash
git status  # See local changes
git fetch && git log HEAD..origin/main --oneline  # See what's new
```

### Tip 2: Use descriptive commit messages
Follow this format:
```
[Type] Short description (50 chars max)

Longer explanation if needed (wrap at 72 chars)

- Bullet points for details
- What changed and why
- Related issues: #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Tip 3: Create aliases for common commands
Add to `~/.bashrc` or `~/.bash_aliases`:
```bash
alias gst='git status'
alias gp='git pull origin main'
alias gpu='git push origin main'
alias gl='git log --oneline -10'
alias gd='git diff'
alias restart-app='pkill -9 -f uvicorn && nohup bash start.sh > /tmp/verbatim-ai.log 2>&1 &'
```

Then run: `source ~/.bashrc`

### Tip 4: Set up systemd service for auto-restart
Instead of manually restarting, create a systemd service:
```bash
sudo nano /etc/systemd/system/verbatim-ai.service
```

```ini
[Unit]
Description=Verbatim AI FastAPI Application
After=network.target

[Service]
Type=simple
User=darko
WorkingDirectory=/var/www/app.quz.ma/verbatim-ai
Environment="PATH=/var/www/app.quz.ma/verbatim-ai/venv/bin"
ExecStart=/var/www/app.quz.ma/verbatim-ai/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable verbatim-ai
sudo systemctl start verbatim-ai
sudo systemctl status verbatim-ai
```

To restart after pulling:
```bash
git pull origin main
sudo systemctl restart verbatim-ai
```

---

## Summary

**Local Development → GitHub:**
```bash
git add . && git commit -m "Message" && git push
```

**GitHub → Production Server:**
```bash
git stash && git pull && pip install -r requirements.txt && restart app
```

**Always verify:**
```bash
curl https://app.quz.ma/verbatim-ai/health
```

---

## Getting Help

- Check git status: `git status`
- View recent commits: `git log --oneline -10`
- See what changed: `git diff`
- Undo last commit (keep changes): `git reset --soft HEAD~1`
- Undo last commit (discard changes): `git reset --hard HEAD~1`
- Get help: `git help <command>`

**Remember:** When in doubt, `git stash` your changes before pulling!
