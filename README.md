# Khmer News Classifier

A machine learning-powered web application for classifying Khmer news articles into different categories using both SVM and FastText models.

## Features

- **Dual Model Support**: Uses both SVM and FastText models for article classification
- **Real-time Classification**: Instant classification of Khmer text input
- **Web Interface**: Clean, responsive Streamlit web interface
- **Multiple Categories**: Classifies articles into various news categories
- **Browser Persistence**: Automatically saves articles in browser local storage
- **Bilingual Support**: Interface supports both Khmer and English

## Models

- **SVM Model**: Lightweight, fast classification using scikit-learn
- **FastText Model**: Deep learning model trained on Khmer text (cc.km.300.bin)
- **Stopword Filtering**: Uses 1000+ Khmer stopwords for better accuracy

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/khmer-news-classifier.git
cd khmer-news-classifier
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download FastText model (optional, ~2.8GB):
```bash
wget -O cc.km.300.vec.gz https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.vec.gz
gunzip cc.km.300.vec.gz
mv cc.km.300.vec cc.km.300.bin
```

5. Run the application:
```bash
streamlit run khmer_news_classifier_pro.py
```

## Deployment to DigitalOcean

### Prerequisites
- DigitalOcean droplet with Ubuntu 20.04+
- Minimum 4GB RAM (recommended for FastText model)
- SSH access configured

### Deploy from GitHub

1. Upload your project to GitHub
2. Use the deployment script:
```bash
./deploy_from_github.sh YOUR_DROPLET_IP https://github.com/YOUR_USERNAME/khmer-news-classifier.git
```

### Update Deployment
```bash
./update_from_github.sh YOUR_DROPLET_IP
```

## Project Structure

```
khmer-news-classifier/
├── khmer_news_classifier_pro.py    # Main Streamlit application
├── requirements.txt                # Python dependencies
├── Demo_model/                     # SVM model files
│   ├── svm_model.joblib
│   └── ...
├── deployment_configs/             # Server configuration files
├── Khmer-Stop-Word-1000.txt       # Khmer stopwords
├── deploy_from_github.sh           # GitHub deployment script
├── update_from_github.sh           # Update script
└── cc.km.300.bin                   # FastText model (downloaded separately)
```

## Technology Stack

- **Backend**: Python, scikit-learn, FastText
- **Frontend**: Streamlit
- **Deployment**: Nginx, SystemD, Ubuntu
- **Models**: SVM (scikit-learn), FastText (Facebook AI)

## API Usage

The application provides a web interface, but you can also use it programmatically:

```python
from khmer_news_classifier_pro import classify_text

# Classify text
result = classify_text("Your Khmer text here")
print(result)
```

## Model Performance

- **SVM Model**: Fast inference, lightweight (~50MB)
- **FastText Model**: Higher accuracy, larger size (~2.8GB)
- **Combined**: Best of both worlds with fallback support

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **FastText model not loading**: The app will work with SVM only if FastText model is unavailable
2. **Memory issues**: Ensure your system has sufficient RAM (4GB+ recommended)
3. **Dependency conflicts**: Use a virtual environment for clean installation

### Support

- Check application logs: `journalctl -u khmer-classifier -f`
- Restart application: `systemctl restart khmer-classifier`
- Update from GitHub: `./update_from_github.sh YOUR_DROPLET_IP`

## Acknowledgments

- FastText model from Facebook AI Research
- Khmer stopwords from various linguistic sources
- Built with Streamlit and scikit-learn

---

**Ready to classify Khmer news! 🇰🇭**
