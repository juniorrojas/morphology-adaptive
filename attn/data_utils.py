import torch
from .frame_projection import project_pos_vel

def make_vertex_and_muscle_keys(mesh_data, center_vertex_id, forward_vertex_id):
    vertex_k = []
    muscle_k = []
    
    pos = torch.tensor(mesh_data["pos"], dtype=torch.float32)
    vel = torch.zeros_like(pos)
    _, projected_pos, projected_vel = project_pos_vel(
        pos, vel,
        center_vertex_id, forward_vertex_id
    )

    muscles = mesh_data["muscles"]
    
    for muscle in muscles:
        i1, i2 = muscle
        p1 = projected_pos[i1]
        p2 = projected_pos[i2]
        pm = (p1 + p2) / 2
        assert pm.shape == (2,)
        muscle_k.append(pm.tolist())

    vertex_k = projected_pos.tolist()

    return vertex_k, muscle_k