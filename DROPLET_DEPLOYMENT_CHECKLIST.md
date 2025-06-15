# Droplet Deployment Checklist for Khmer News Classifier

## Pre-Deployment Requirements

### 1. DigitalOcean Droplet Setup

- [ ] Droplet created with Ubuntu 20.04+ LTS
- [ ] Minimum 2GB RAM (recommended 4GB for FastText model)
- [ ] SSH access configured
- [ ] Firewall allows HTTP (port 80) and HTTPS (port 443)
- [ ] Root or sudo access available

### 2. Local Environment

- [ ] SSH key configured for droplet access
- [ ] All required files present in `/Users/socheata/Documents/DEV/`:
  - [ ] `khmer_news_classifier_pro.py`
  - [ ] `requirements.txt`
  - [ ] `Demo_model/` directory with SVM model files
  - [ ] `Khmer-Stop-Word-1000.txt`
  - [ ] `deployment_configs/` directory
  - [ ] FastText model (`cc.km.300.bin`) will be downloaded on server

### 3. Network Access

- [ ] SSH connection to droplet working
- [ ] Droplet has internet access for FastText model download

## Deployment Steps

### Step 1: Test SSH Connection

```bash
ssh root@YOUR_DROPLET_IP
```

### Step 2: Run Upload Script

```bash
cd /Users/socheata/Documents/DEV
./upload_to_droplet.sh YOUR_DROPLET_IP root
```

### Step 3: Verify Deployment

1. Check if service is running:

   ```bash
   ssh root@YOUR_DROPLET_IP 'systemctl status khmer-classifier'
   ```

2. Test application access:

   ```bash
   curl http://YOUR_DROPLET_IP
   ```

3. Check logs if needed:
   ```bash
   ssh root@YOUR_DROPLET_IP 'journalctl -u khmer-classifier -f'
   ```

## Post-Deployment Configuration

### Optional: Set Up SSL Certificate

```bash
ssh root@YOUR_DROPLET_IP 'cd /opt/khmer-news-classifier/deployment_configs && ./setup_ssl.sh YOUR_DOMAIN'
```

### Monitor Application

```bash
ssh root@YOUR_DROPLET_IP 'cd /opt/khmer-news-classifier/deployment_configs && ./monitor.sh'
```

## Troubleshooting

### Common Issues:

1. **FastText download failure**: Model downloads directly on server, check internet connection
2. **Memory issues**: Ensure droplet has sufficient RAM (4GB recommended)
3. **Permission errors**: Script sets proper permissions automatically
4. **Port conflicts**: Script uses port 8501 for Streamlit, 80 for nginx

### Re-download FastText Model:

```bash
cd /Users/socheata/Documents/DEV
./download_fasttext_model.sh YOUR_DROPLET_IP root
```

### Manual Restart:

```bash
ssh root@YOUR_DROPLET_IP 'systemctl restart khmer-classifier'
```

### Update Application:

```bash
ssh root@YOUR_DROPLET_IP 'cd /opt/khmer-news-classifier/deployment_configs && ./update.sh'
```

## File Structure on Droplet

```
/opt/khmer-news-classifier/
├── khmer_news_classifier_pro.py
├── requirements.txt
├── packages.txt
├── Demo_model/
│   ├── svm_model.joblib
│   └── ...
├── cc.km.300.bin
├── Khmer-Stop-Word-1000.txt
├── venv/
├── deployment_configs/
└── metadata.csv
```

## Service Management

- **Start**: `systemctl start khmer-classifier`
- **Stop**: `systemctl stop khmer-classifier`
- **Restart**: `systemctl restart khmer-classifier`
- **Status**: `systemctl status khmer-classifier`
- **Logs**: `journalctl -u khmer-classifier -f`

## Security Notes

- Application runs as `www-data` user
- Nginx reverse proxy handles external requests
- No database credentials needed (browser storage only)
- All ML models stored locally on server
