# SSL Certificate Management

This document explains how SSL certificates are handled in the Khmer News Classifier project.

## Security Note

**SSL certificates and private keys are NOT stored in the GitHub repository for security reasons.** 

The following files are excluded from git tracking via `.gitignore`:
- `*.crt` (Certificate files)
- `*.ca-bundle` (Certificate Authority bundles)
- `*.key` (Private key files)
- `*_csr.txt` (Certificate Signing Request files)
- `server_csr.txt`
- `khnewsclassifier_tech.ca-bundle`
- `khnewsclassifier_tech.crt`
- `server.key`

## SSL Certificate Files

The project expects these SSL certificate files:

1. **khnewsclassifier_tech/khnewsclassifier_tech.crt** - SSL certificate
2. **khnewsclassifier_tech/khnewsclassifier_tech.ca-bundle** - Certificate Authority bundle
3. **server.key** - Private key
4. **server_csr.txt** - Certificate Signing Request (for reference)

## Deployment Process

### 1. Deploy Application (HTTP only)
```bash
./deploy_from_github.sh [github_repo] [server_ip] [ssh_user]
```

This script:
- Clones the repository from GitHub
- Sets up the application with HTTP access
- Does NOT include SSL certificates

### 2. Upload SSL Certificates Separately
```bash
./upload_ssl_certs.sh [server_ip] [ssh_user]
```

This script:
- Uploads SSL certificates directly to the server
- Creates SSL-enabled nginx configuration
- Optionally enables HTTPS immediately

## Example Usage

```bash
# Deploy the application
./deploy_from_github.sh username/khmer-news-classifier 192.168.1.100 root

# Upload SSL certificates
./upload_ssl_certs.sh 192.168.1.100 root
```

## SSL Certificate Setup on Server

The SSL upload script places certificates in `/etc/nginx/ssl/` with proper permissions:

```
/etc/nginx/ssl/
├── khnewsclassifier_tech.crt          (644)
├── khnewsclassifier_tech.ca-bundle    (644)
├── server.key                         (600)
├── server_csr.txt                     (644)
└── fullchain.crt                      (644) - Combined cert + CA bundle
```

## Nginx SSL Configuration

The script creates two nginx configurations:

1. **HTTP only** (default): `/etc/nginx/sites-available/khmer-classifier`
2. **HTTPS with redirect**: `/etc/nginx/sites-available/khmer-classifier-ssl`

To switch between configurations:

```bash
# Enable HTTP only
sudo ln -sf /etc/nginx/sites-available/khmer-classifier /etc/nginx/sites-enabled/khmer-classifier
sudo systemctl reload nginx

# Enable HTTPS with HTTP redirect
sudo ln -sf /etc/nginx/sites-available/khmer-classifier-ssl /etc/nginx/sites-enabled/khmer-classifier
sudo systemctl reload nginx
```

## Certificate Renewal

When SSL certificates need renewal:

1. Obtain new certificate files locally
2. Run the upload script again:
   ```bash
   ./upload_ssl_certs.sh [server_ip] [ssh_user]
   ```
3. The script will automatically reload nginx

## Troubleshooting SSL

### Check certificate validity
```bash
ssh user@server 'openssl x509 -in /etc/nginx/ssl/khnewsclassifier_tech.crt -text -noout'
```

### Test SSL configuration
```bash
ssh user@server 'nginx -t'
```

### Check SSL logs
```bash
ssh user@server 'tail -f /var/log/nginx/error.log'
```

### Verify SSL setup
```bash
curl -I https://your-domain.com
```

## Security Best Practices

1. **Never commit SSL certificates to git**
2. **Store certificates securely** on your local machine
3. **Use secure file transfer** (SCP/SFTP) for uploading certificates
4. **Set proper file permissions** (600 for private keys, 644 for certificates)
5. **Regularly renew certificates** before expiration
6. **Monitor certificate expiration dates**

## File Locations

### Local Development
- SSL files should be in the project root directory
- Files are automatically ignored by git

### Production Server
- SSL files: `/etc/nginx/ssl/`
- Nginx config: `/etc/nginx/sites-available/`
- Application: `/opt/khmer-news-classifier/`

## Support

If you encounter SSL issues:

1. Check that all certificate files exist locally
2. Verify SSH access to the server
3. Ensure proper file permissions
4. Test nginx configuration
5. Check nginx error logs
