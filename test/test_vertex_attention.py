import attn
import torch
torch.manual_seed(0)

def test_vertex_attention_shapes():
    batch_size, num_vertices, vertex_key_size = 2, 3, 4
    vertex_value_size = 5
    num_queries = 6
    num_heads = 7
    k = torch.randn(batch_size, num_vertices, vertex_key_size, dtype=torch.float32)
    v = torch.randn(batch_size, num_vertices, vertex_value_size, dtype=torch.float32)
    q = torch.randn(batch_size, num_queries, num_heads, vertex_key_size, dtype=torch.float32)
    wv = attn.vertex_attention(k, v, q)
    assert wv.shape == (batch_size, num_queries, num_heads, vertex_value_size)

def test_mask_1():
    vertex_key = torch.tensor([
        [3, 4],
        [5, 10],
        [9, 11]
    ], dtype=torch.float32).unsqueeze(0)
    vertex_value = torch.tensor([
        [3, 4],
        [5, 10],
        [9, 11]
    ], dtype=torch.float32).unsqueeze(0)
    query = torch.tensor([
        [31, 40],
        [0, 0]
    ], dtype=torch.float32).unsqueeze(0)
    mask = torch.tensor([
        [1, 0, 0]
    ], dtype=torch.float32)
    wv = attn.vertex_attention(vertex_key, vertex_value, query, mask=mask)
    torch.testing.assert_close(wv, torch.tensor([[[3, 4], [3, 4]]], dtype=torch.float32).unsqueeze(0))

def test_mask_2():
    vertex_key = torch.tensor([
        [3, 4],
        [5, 10],
        [9, 11]
    ], dtype=torch.float32).unsqueeze(0)
    vertex_value = torch.tensor([
        [3, 4],
        [5, 10],
        [9, 11]
    ], dtype=torch.float32).unsqueeze(0)
    query = torch.tensor([
        [31, 40],
        [0, 0],
        [-10, -2],
        [-20, 20]
    ], dtype=torch.float32).unsqueeze(0)
    mask = torch.tensor([
        [0, 1, 0]
    ], dtype=torch.float32)
    wv = attn.vertex_attention(vertex_key, vertex_value, query, mask=mask)
    torch.testing.assert_close(wv, torch.tensor([[[5, 10], [5, 10], [5, 10], [5, 10]]], dtype=torch.float32).unsqueeze(0))

def test_vertex_attention_values():
    vertex_key = torch.tensor([
        [1, 0.4],
        [-1, 0]
    ], dtype=torch.float32).unsqueeze(0)
    vertex_value = torch.tensor([
        [3, 4],
        [9, 5]
    ], dtype=torch.float32).unsqueeze(0)
    query = torch.tensor([
        [2, 0],
        [-0.3, 0.1]
    ], dtype=torch.float32).unsqueeze(0)
    wv = attn.vertex_attention(vertex_key, vertex_value, query)
    torch.testing.assert_close(
        wv,
        torch.tensor([[
            [
                [3.1079172597725497, 4.017986209962092],
                [6.818715241689398, 4.636452540281566]
            ]
        ]], dtype=torch.float32)
    )