import requests
import os

def download_file(url, filename):
    print(f"Downloading {url} to {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {filename}")

if __name__ == "__main__":
    url = "https://media.githubusercontent.com/media/anasouzac/new_tep_datasets/main/python_data_1year.csv"
    output_path = "data/python_data_1year.csv"
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    download_file(url, output_path)
