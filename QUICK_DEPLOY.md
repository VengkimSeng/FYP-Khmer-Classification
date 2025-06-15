# Quick Deployment Guide

## Ready to Deploy! 🚀

Your Khmer News Classifier is ready for deployment to your DigitalOcean droplet.

### What You Need:

1. **Your Droplet IP Address** - Get this from your DigitalOcean dashboard
2. **SSH Access** - Make sure you can SSH to your droplet

### Deploy in 3 Simple Steps:

#### Step 1: Get Your Droplet IP

- Log into your DigitalOcean dashboard
- Find your droplet's public IP address
- Example: `192.168.1.100`

#### Step 2: Deploy the Application

```bash
cd /Users/socheata/Documents/DEV
./upload_to_droplet.sh YOUR_DROPLET_IP root
```

Replace `YOUR_DROPLET_IP` with your actual IP address.

#### Step 3: Access Your Application

- Open your browser
- Go to: `http://YOUR_DROPLET_IP`
- Your Khmer News Classifier should be running!

### Example Deployment Command:

```bash
./upload_to_droplet.sh 192.168.1.100 root
```

### What the Script Does:

1. ✅ Tests SSH connection
2. ✅ Creates application directory structure
3. ✅ Uploads application files (no FastText model upload)
4. ✅ Installs Python dependencies
5. ✅ Downloads FastText model directly on server
6. ✅ Sets up systemd service
7. ✅ Configures nginx reverse proxy
8. ✅ Starts the application
9. ✅ Verifies deployment

### Deployment Time:

- **File uploads**: ~2-3 minutes
- **FastText model download**: ~10-20 minutes (server downloads directly)
- **Total**: ~15-25 minutes

### Advantages of Server-Side Download:

- 🚀 **Faster deployment** - No need to upload 2.8GB model
- 💰 **Saves bandwidth** - Server downloads directly from FastText
- 🔄 **More reliable** - Server has better connection than your laptop

### After Deployment:

- Your app will be accessible at `http://YOUR_DROPLET_IP`
- All browser storage functionality will work
- Application auto-starts on server reboot
- Logs available via: `journalctl -u khmer-classifier -f`

### Troubleshooting:

If something goes wrong, check the detailed guide in `DROPLET_DEPLOYMENT_CHECKLIST.md`

### Optional: Set Up Domain & SSL

After deployment, you can:

1. Point a domain to your droplet IP
2. Set up SSL certificate using the included scripts

**You're all set! Run the deployment command when ready.**
