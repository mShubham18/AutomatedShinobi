import io
import urllib.request
from duckduckgo_search import DDGS
from PIL import Image, ImageOps
from model_configuration import model_config


class ImageGeneration:
    def __init__(self):
        self.model = model_config()
    def generate_image(self,excerpt):

        prompt=f"""Consider this excerpt: {excerpt}
        Retrieve the list of keywords that i could feed into duckduckgo search api to get clean mobile sized photos regarding the excerpt
        just a single line with comma seperated values.
        modify the keywords such that it only fetches mobile sized imamges. like modifiyinh the output words like output+  mobile wallpaper, etc for example if the list has word as eifil tower, give the response loke eifil tower mobile wallpaper but keep in mind alwyays add the word bleach as a prefix
        etc

        i only want the response, i do not need any salutation"""
        keywords = self.model.generate_content(prompt)
        return keywords.text


    def get_duckduckgo_images(self,query, num_images=30):
        image_list = []
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=num_images)

        for i, img in enumerate(results):
            try:
                image_url = img["image"]
                image_data = urllib.request.urlopen(image_url).read()
                image = Image.open(io.BytesIO(image_data))

                # Convert to 9:16 with padding
                image = self.convert_to_9_16_with_padding(image)

                image_list.append(image)
                print(f"Processed Image {i+1}: {image_url} (Size: {image.size})")
            except Exception as e:
                print(f"Error downloading {image_url}: {e}")

        return image_list

    def convert_to_9_16_with_padding(self,image, target_width=1080, target_height=1920):
        """ Convert image to 9:16 aspect ratio using padding instead of cropping """
        width, height = image.size
        target_aspect = 9 / 16
        image_aspect = width / height

        if image_aspect > target_aspect:
            # Image is too wide, add padding to top/bottom
            new_height = int(width / target_aspect)
            padded_image = Image.new("RGB", (width, new_height), (0, 0, 0))  # Black background
            padded_image.paste(image, (0, (new_height - height) // 2))
        else:
            # Image is too tall, add padding to left/right
            new_width = int(height * target_aspect)
            padded_image = Image.new("RGB", (new_width, height), (0, 0, 0))  # Black background
            padded_image.paste(image, ((new_width - width) // 2, 0))

        # Resize to final 1080x1920 resolution
        final_image = padded_image.resize((target_width, target_height), Image.LANCZOS)
        return final_image

# Example Usage

obj = ImageGeneration()
query = "Bleach Aizen Soul King Royal Realm"
excerpt = "Remember when Aizen was all about transcending? Did you know that in the light novels, it's revealed that his ultimate goal wasn't just power, but to create a key, a king's key capable of opening the gates to the Royal Realm without needing the ritual involving the souls of one hundred thousand people from Rukongai. In other words, Aizen wanted to dethrone the Soul King not for absolute power, but to change the very system. He wanted to find a different way to open the realm. "
keywords = obj.generate_image(excerpt)
mobile_images = obj.get_duckduckgo_images(keywords, num_images=5)
print(f"Total Processed Images: {len(mobile_images)}")
