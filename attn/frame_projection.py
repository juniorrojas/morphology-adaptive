import torch

def normalize2d(vx, vy):
    q = vx * vx + vy * vy
    norm = q.sqrt()
    if q.item() == 0:
        return 1.0, 0.0
    return vx / norm, vy / norm

def dot2d(ax, ay, bx, by):
    return ax * bx + ay * by

def frame_projection(pos, center_vertex_id, forward_vertex_id, data, subtract_origin):
    space_dim = 2
    assert len(pos.shape) == 2
    assert pos.shape[1] == space_dim
    assert len(data.shape) == 2

    assert pos.shape[0] == data.shape[0]

    num_vertices = pos.shape[0]
    projected_data = torch.empty_like(data)
    cx, cy = pos[center_vertex_id]
    fx, fy = pos[forward_vertex_id]

    ax = fx - cx
    ay = fy - cy
    ax, ay = normalize2d(ax, ay)
    bx = -ay
    by = ax

    for i in range(num_vertices):
        px = data[i, 0].item()
        py = data[i, 1].item()
        if subtract_origin:
            px = px - cx
            py = py - cy
        projected_data[i, 0] = dot2d(ax, ay, px, py)
        projected_data[i, 1] = dot2d(bx, by, px, py)
    
    return projected_data

def project_pos_vel(pos, vel, center_vertex_id, forward_vertex_id):
    projected_pos = frame_projection(
        pos, center_vertex_id, forward_vertex_id,
        pos,
        subtract_origin=True
    )
    projected_vel = frame_projection(
        pos, center_vertex_id, forward_vertex_id,
        vel,
        subtract_origin=False
    )
    num_vertices = pos.shape[0]
    assert projected_pos.shape == (num_vertices, 2)
    assert projected_vel.shape == (num_vertices, 2)
    policy_input = torch.stack([projected_pos, projected_vel]).view(-1).contiguous()
    assert policy_input.shape == (pos.shape[0] * 4,)
    return policy_input, projected_pos, projected_vel