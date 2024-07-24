import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

def fetch_apod_image(api_key):
    """
    Fetch the Astronomy Picture of the Day from NASA's API.

    Parameters:
    api_key (str): Your NASA API key.

    Returns:
    Image data in bytes or None if an error occurs.
    """
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data.get('url')
        if image_url:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                return image_response.content
            else:
                print(f"Error fetching image: {image_response.status_code} - {image_response.text}")
                return None
        else:
            print("No image URL found in the API response.")
            return None
    else:
        print(f"Error fetching APoD data: {response.status_code} - {response.text}")
        return None

def display_image(image_data):
    """
    Display the image using matplotlib.

    Parameters:
    image_data: Image data in bytes.
    """
    image = Image.open(BytesIO(image_data))
    plt.imshow(image)
    plt.axis('off')  # Hide axes
    plt.show()

def main():
    api_key = input("Enter your NASA API key: ")
    image_data = fetch_apod_image(api_key)
    if image_data:
        display_image(image_data)

if __name__ == "__main__":
    main()
