import attn
import torch
torch.manual_seed(0)

def test_frame_projection():
    space_dim = 2
    num_vertices = 9
    pos = torch.randn(num_vertices, space_dim, dtype=torch.float32)
    
    center_vertex_id = 0
    forward_vertex_id = 1
    
    projection = attn.frame_projection(
        pos,
        center_vertex_id,
        forward_vertex_id,
        pos,
        True
    )

    assert projection.shape == (num_vertices, space_dim)