import attn
import torch
torch.manual_seed(0)

def test_model():
    batch_size = 7
    
    num_muscles = 5
    num_vertices = 8

    key_size = 2
    value_size = 4

    model = attn.Model(
        vertex_value_size=value_size
    )

    vertex_k = torch.randn(batch_size, num_vertices, key_size)
    vertex_v = torch.randn(batch_size, num_vertices, value_size)
    muscle_k = torch.randn(batch_size, num_muscles, key_size)

    da = model(vertex_k, muscle_k, vertex_v)
    assert da.shape == (batch_size, num_muscles)