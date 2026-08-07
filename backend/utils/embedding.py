# Functions related to:
# 1. Loading the Fashion SigLIP model
# 2. Preprocessing images
# 3. Generating embeddings
# 4. Saving and loading embeddings



# only job: Image → Embedding



import os
import numpy as np
import torch
from PIL import Image
import open_clip
from tqdm import tqdm



IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
)


def get_catalogue_images(root_folder):
    image_paths = []
    for root, dirs, files in os.walk(root_folder):

        for file in files:

            if file.lower().endswith(IMAGE_EXTENSIONS):

                full_path = os.path.join(root, file)

                image_paths.append(full_path)

    image_paths.sort()
    return image_paths



def load_image(image_path):
    image = Image.open(image_path)
    image = image.convert("RGB")

    return image



def preprocess_image(image, preprocess, device):
    if image.mode != "RGB":
        image = image.convert("RGB")

    image = preprocess(image)

    image = image.unsqueeze(0)

    image = image.to(device)

    return image

def get_image_embedding(model, inputs):

    with torch.no_grad():
        embedding = model.encode_image(inputs)

    embedding = embedding.cpu().numpy()

    return embedding





def generate_catalogue_embeddings(catalogue,model,preprocess,device):
    embeddings = []

    for image_path in tqdm(catalogue, desc="Generating Embeddings"):

        image = load_image(image_path)

        inputs = preprocess_image(
            image,
            preprocess,
            device
        )

        embedding = get_image_embedding(
            model,
            inputs
        )

        embeddings.append(embedding[0])
    embeddings = np.array(embeddings)

    return embeddings


