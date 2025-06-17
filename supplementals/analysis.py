from torchviz import make_dot
from torchinfo import summary
import torch
from torchvision.models import mobilenet_v2

model_path = "../../dial_model_100class_mobilenet_best.pt"
model = torch.load(model_path, map_location='cpu')

model = mobilenet_v2(num_classes=100)
model.load_state_dict(torch.load(model_path, map_location='cpu'))

summary(model, input_size=(1, 3, 224, 224))

dummy_input = torch.randn(1, 3, 224, 224)
output = model(dummy_input)
make_dot(output, params=dict(model.named_parameters())).render("model", format="png")

total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")