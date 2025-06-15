# GitHub Deployment Guide

## 🚀 Deploy via GitHub (Recommended)

This method is cleaner, more reliable, and follows modern DevOps practices.

### Benefits of GitHub Deployment:

- ✅ **Version Control**: Track all changes
- ✅ **No Large File Uploads**: FastText model downloaded on server
- ✅ **Easy Updates**: Simple `git pull` to update
- ✅ **Backup**: Your code is safely stored on GitHub
- ✅ **Collaboration**: Easy to share and collaborate

## Step-by-Step Deployment

### 1. Upload to GitHub

```bash
cd /Users/socheata/Documents/DEV

# Add all files (large files are already in .gitignore)
git add .
git commit -m "Initial commit - Khmer News Classifier"

# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/khmer-news-classifier.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Droplet

```bash
./deploy_from_github.sh YOUR_DROPLET_IP https://github.com/YOUR_USERNAME/khmer-news-classifier.git
```

**Example:**

```bash
./deploy_from_github.sh 192.168.1.100 https://github.com/socheata/khmer-news-classifier.git root
```

### 3. Access Your App

Open browser: `http://YOUR_DROPLET_IP`

## Future Updates

### Update Your Code:

1. Make changes locally
2. Commit and push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

### Update Server:

```bash
./update_from_github.sh YOUR_DROPLET_IP
```

## What Gets Deployed:

### ✅ Included in GitHub:

- Application code (`khmer_news_classifier_pro.py`)
- Requirements (`requirements.txt`)
- SVM model files (`Demo_model/`)
- Deployment scripts
- Configuration files
- Documentation

### ❌ Excluded from GitHub (.gitignore):

- Large data files (`raw_articles/`, `preprocessed_articles/`)
- FastText model (`cc.km.300.bin`) - downloaded on server
- Virtual environment (`.venv/`)
- Cache files and logs

## Deployment Process:

1. **Clone from GitHub** (~30 seconds)
2. **Install dependencies** (~2-3 minutes)
3. **Download FastText model** (~10-15 minutes)
4. **Configure services** (~1-2 minutes)
5. **Start application** (~30 seconds)

**Total time: ~15-20 minutes**

## Troubleshooting:

### If deployment fails:

```bash
# Check what went wrong
ssh root@YOUR_DROPLET_IP 'journalctl -u khmer-classifier -f'

# Retry deployment
./deploy_from_github.sh YOUR_DROPLET_IP https://github.com/YOUR_USERNAME/repo.git
```

### If FastText download fails:

```bash
# The app will still work with SVM model only
# Or manually download FastText later:
./download_fasttext_model.sh YOUR_DROPLET_IP
```

## Security Notes:

- Use SSH keys instead of passwords
- Consider setting up a non-root user
- Configure firewall (UFW) for additional security
- Set up SSL certificate for HTTPS

## Repository Structure:

Your GitHub repository will contain:

```
khmer-news-classifier/
├── README.md                       # Project documentation
├── khmer_news_classifier_pro.py    # Main application
├── requirements.txt                # Python dependencies
├── .gitignore                     # Excluded files
├── Demo_model/                    # SVM model files
├── deployment_configs/            # Server configs
├── deploy_from_github.sh          # Deployment script
├── update_from_github.sh          # Update script
├── Khmer-Stop-Word-1000.txt      # Stopwords
└── documentation/                 # Deployment guides
```

---

**This approach is much cleaner than direct file uploads and follows modern deployment practices! 🎉**
