import os
import requests

def download_fasttext_model(url: str, output_path: str):
    """Download the FastText model from the given URL."""
    if os.path.exists(output_path):
        print(f"File already exists at {output_path}. Skipping download.")
        return

    print(f"Downloading FastText model from {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Download complete. Model saved to {output_path}.")
    else:
        print(f"Failed to download the model. HTTP Status Code: {response.status_code}")

if __name__ == "__main__":
    # URL of the FastText model
    model_url = "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.bin.gz"
    # Path to save the downloaded model
    output_file = "cc.km.300.bin.gz"

    download_fasttext_model(model_url, output_file)