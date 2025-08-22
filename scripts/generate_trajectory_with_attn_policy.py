import os
import shutil
from pathlib import Path
import torch
this_filepath = Path(os.path.realpath(__file__))
this_dirpath = this_filepath.parent
import json
import argparse
import time
import attn
import algovivo

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--steps", type=int, default=100)
    arg_parser.add_argument("--agent", type=str, required=False)
    arg_parser.add_argument("--mesh", type=str)
    arg_parser.add_argument("--policy-metadata", type=str)
    arg_parser.add_argument("--policy", type=str)
    arg_parser.add_argument("--output", "-o", type=str, default="trajectory_attn.out")

    args = arg_parser.parse_args()

    if args.agent is not None:
        agent_filename = args.agent
        mesh_filename = os.path.join(args.agent, "mesh.json")
        policy_metadata_filename = os.path.join(args.agent, "policy_metadata.json")
        if not os.path.exists(policy_metadata_filename):
            policy_metadata_filename = os.path.join(args.agent, "policy.json")
    else:
        policy_metadata_filename = args.policy_metadata
        assert policy_metadata_filename is not None, "policy metadata must be provided if agent is not provided"
        mesh_filename = args.mesh
        assert mesh_filename is not None, "mesh must be provided if agent is not provided"

    with open(policy_metadata_filename) as f:
        policy_data = json.load(f)
        center_vertex_id = policy_data["center_vertex_id"]
        forward_vertex_id = policy_data["forward_vertex_id"]
        max_abs_da = policy_data["max_abs_da"]
        min_a = policy_data["min_a"]

    with open(mesh_filename) as f:
        mesh_data = json.load(f)

    vertex_k, muscle_k = attn.make_vertex_and_muscle_keys(mesh_data, policy_data)

    native_instance = algovivo.NativeInstance.load(
        str(this_dirpath.parent.joinpath("build", "algovivo.so"))
    )

    num_vertices = len(mesh_data["pos"])

    model = attn.Model.load(args.policy)

    system = algovivo.System(native_instance)
    system.set(
        pos=mesh_data["pos"],
        triangles=mesh_data["triangles"],
        triangles_rsi=mesh_data.get("rsi"),
        muscles=mesh_data["muscles"],
        muscles_l0=mesh_data.get("l0"),
    )

    vertex_k = torch.tensor(vertex_k, dtype=torch.float32).unsqueeze(0)
    muscle_k = torch.tensor(muscle_k, dtype=torch.float32).unsqueeze(0)

    traj_output_dirpath = Path(args.output)
    steps_dirpath = traj_output_dirpath.joinpath("steps")

    shutil.rmtree(traj_output_dirpath, ignore_errors=True)
    os.makedirs(traj_output_dirpath, exist_ok=True)
    os.makedirs(steps_dirpath, exist_ok=True)

    with open(traj_output_dirpath.joinpath("mesh.json"), "w") as f:
        json.dump(mesh_data, f)

    sim_step_time = 0.0 # time spent on simulation steps only

    for i in range(args.steps):
        print(i)

        # state before policy and simulation step
        pos0 = system.vertices.pos.detach().tolist()
        vel0 = system.vertices.vel.detach().tolist()
        a0 = system.muscles.a.detach().tolist()
        
        # run policy (pos, vel) -> da
        _, projected_pos, projected_vel = attn.project_pos_vel(
            system.vertices.pos, system.vertices.vel,
            center_vertex_id, forward_vertex_id
        )
        batch_size = 1
        assert vertex_k.shape == (batch_size, num_vertices, 2)
        vertex_v = torch.cat([projected_pos, projected_vel], dim=1).unsqueeze(0)
        assert vertex_v.shape == (batch_size, num_vertices, 4)
        da = model(vertex_k, muscle_k, vertex_v)
        da = da.clamp(min=-max_abs_da, max=max_abs_da)[0]

        # update a with da
        system.muscles.a += da
        system.muscles.a.clamp_(min=min_a, max=1)

        # start timing simulation step
        sim_step_start_time = time.time()

        # update simulation
        system.step()

        # end timing simulation step
        sim_step_end_time = time.time()
        sim_step_time += sim_step_end_time - sim_step_start_time

        # state after policy and simulation step
        pos1 = system.vertices.pos.detach().tolist()
        vel1 = system.vertices.vel.detach().tolist()
        a1 = system.muscles.a.detach().tolist()

        # save step data
        with open(steps_dirpath.joinpath(f"{i}.json"), "w") as f:
            json.dump({
                "pos0": pos0,
                "vel0": vel0,
                "a0": a0,
                "pos1": pos1,
                "vel1": vel1,
                "a1": a1
            }, f)

    print(f"trajectory saved to {traj_output_dirpath}")

    print(f"simulation step time: {sim_step_time:.3f} seconds")