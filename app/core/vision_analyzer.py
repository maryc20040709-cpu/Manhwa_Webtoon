import requests

class VisionAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = "https://api.claude.vision/analyze"

    def analyze_image(self, image_path):
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.post(self.endpoint, headers=headers, files=files)
            return response.json()

# Sample usage:
# if __name__ == "__main__":
#     analyzer = VisionAnalyzer(api_key="your_api_key_here")
#     result = analyzer.analyze_image("path_to_image.jpg")
#     print(result)