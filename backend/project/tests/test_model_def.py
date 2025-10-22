import torch
from backend.model_def import ProjectileNet

def test_forward_shape():
    model = ProjectileNet()
    x = torch.randn(5, 2)
    y = model(x)
    assert y.shape == (5, 3)
