import torch
from torchvision import transforms, models
from PIL import Image
import torch.nn as nn

# Load MobileNetV2 architecture
model = models.mobilenet_v2(weights=None)  # No pretrained weights
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 100)  # 100 output classes

# Load your trained weights
model.load_state_dict(torch.load("../dial_model_100class_mobilenet_best.pt", map_location='cpu'))
model.eval()

# Image transformation (must match training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to model input size
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def classify_image(image_path):
    """
    Classify an image and return predicted class index (0–99).
    """
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0)  # Add batch dimension
    with torch.no_grad():
        output = model(tensor)
        prediction = output.argmax(dim=1).item()
    return prediction
