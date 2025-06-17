import torch
from torchvision.models import mobilenet_v2
from torchviz import make_dot

# Load your model's state_dict
state_dict = torch.load("../../dial_model_100class_mobilenet_best.pt", map_location='cpu')

# Define architecture and load weights
model = mobilenet_v2(num_classes=100)
model.load_state_dict(state_dict)
model.eval()

# Create dummy input
dummy_input = torch.randn(1, 3, 224, 224)

# Forward pass and render graph
output = model(dummy_input)
dot = make_dot(output, params=dict(model.named_parameters()))
dot.render("mobilenet_graph", format="png")  # Generates mobilenet_graph.png