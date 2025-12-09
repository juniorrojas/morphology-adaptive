import attn
import torch
torch.manual_seed(0)

def test_model_shapes():
    batch_size = 7

    num_muscles = 5
    num_vertices = 8

    key_size = 2
    value_size = 4

    model = attn.Model(
        vertex_value_size=value_size,
        muscle_key_size=key_size,
        vertex_key_size=key_size
    )

    vertex_k = torch.randn(batch_size, num_vertices, key_size)
    vertex_v = torch.randn(batch_size, num_vertices, value_size)
    muscle_k = torch.randn(batch_size, num_muscles, key_size)

    da = model(vertex_k, muscle_k, vertex_v)
    assert da.shape == (batch_size, num_muscles)

def test_model_shapes_with_different_key_sizes():
    batch_size = 7
    num_muscles = 5
    num_vertices = 8

    # muscle and vertex key sizes can be different because
    # model.muscle_k_to_vertex_q projects muscle keys to vertex queries
    muscle_key_size = 3
    vertex_key_size = 4

    value_size = 6

    model = attn.Model(
        vertex_value_size=value_size,
        muscle_key_size=muscle_key_size,
        vertex_key_size=vertex_key_size
    )

    vertex_k = torch.randn(batch_size, num_vertices, vertex_key_size)
    vertex_v = torch.randn(batch_size, num_vertices, value_size)
    muscle_k = torch.randn(batch_size, num_muscles, muscle_key_size)

    da = model(vertex_k, muscle_k, vertex_v)
    assert da.shape == (batch_size, num_muscles)