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

    arg_parser.add_argument("--state0", type=str)
    
    arg_parser.add_argument("--policy", type=str)

    arg_parser.add_argument("--policy-metadata", type=str)
    arg_parser.add_argument("--center-vertex-id", type=int)
    arg_parser.add_argument("--forward-vertex-id", type=int)
    arg_parser.add_argument("--max-abs-da", type=float, default=0.3)
    arg_parser.add_argument("--min-a", type=float, default=0.25)

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
        mesh_filename = args.mesh
        assert mesh_filename is not None, "mesh must be provided if agent is not provided"

    # load policy metadata either from file or from args
    if policy_metadata_filename is not None:
        with open(policy_metadata_filename) as f:
            policy_data = json.load(f)
            center_vertex_id = policy_data["center_vertex_id"]
            forward_vertex_id = policy_data["forward_vertex_id"]
            max_abs_da = policy_data["max_abs_da"]
            min_a = policy_data["min_a"]
    else:
        center_vertex_id = args.center_vertex_id
        forward_vertex_id = args.forward_vertex_id
        max_abs_da = args.max_abs_da
        min_a = args.min_a

    with open(mesh_filename) as f:
        mesh_data = json.load(f)

    vertex_k, muscle_k = attn.make_vertex_and_muscle_keys(
        mesh_data,
        center_vertex_id=center_vertex_id,
        forward_vertex_id=forward_vertex_id
    )

    native_instance = algovivo.NativeInstance.load(os.environ["ALGOVIVO_NATIVE_LIB_FILENAME"])

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

    if args.state0 is not None:
        with open(args.state0, "r") as f:
            state0 = json.load(f)
        system.vertices.pos.data.copy_(torch.tensor(state0["pos"]))
        if "vel" in state0:
            system.vertices.vel.data.copy_(torch.tensor(state0["vel"]))
        if "a" in state0:
            system.muscles.a.data.copy_(torch.tensor(state0["a"]))
    
    vertex_k = torch.tensor(vertex_k, dtype=torch.float32).unsqueeze(0)
    muscle_k = torch.tensor(muscle_k, dtype=torch.float32).unsqueeze(0)

    trajectory_output_dirpath = Path(args.output)
    steps_dirpath = trajectory_output_dirpath.joinpath("steps")

    shutil.rmtree(trajectory_output_dirpath, ignore_errors=True)
    os.makedirs(trajectory_output_dirpath, exist_ok=True)
    os.makedirs(steps_dirpath, exist_ok=True)

    with open(trajectory_output_dirpath.joinpath("mesh.json"), "w") as f:
        json.dump(mesh_data, f)

    sim_step_time = 0.0 # time spent on simulation steps only
    policy_step_time = 0.0 # time spent on policy steps only

    num_steps = args.steps

    for i in range(num_steps):
        print(i)

        # state before policy and simulation step
        pos0 = system.vertices.pos.detach().tolist()
        vel0 = system.vertices.vel.detach().tolist()
        a0 = system.muscles.a.detach().tolist()

        # start timing policy step
        policy_step_start_time = time.time()

        # run policy (pos, vel) -> da -> a
        _, projected_pos, projected_vel = attn.project_pos_vel(
            system.vertices.pos, system.vertices.vel,
            center_vertex_id, forward_vertex_id
        )
        batch_size = 1
        assert vertex_k.shape == (batch_size, num_vertices, 2)
        vertex_v = torch.cat([projected_pos, projected_vel], dim=1).unsqueeze(0)
        assert vertex_v.shape == (batch_size, num_vertices, 4)
        da = model(vertex_k, muscle_k, vertex_v)
        policy_output = da[0].detach().tolist() # save before clamping

        # update a with clamped da
        da = da.clamp(min=-max_abs_da, max=max_abs_da)[0]
        system.muscles.a += da
        system.muscles.a.clamp_(min=min_a, max=1)

        # end timing policy step
        policy_step_end_time = time.time()
        policy_step_time += policy_step_end_time - policy_step_start_time

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

                "policy_output": policy_output,

                "pos1": pos1,
                "vel1": vel1,
                "a1": a1
            }, f)

    print(f"trajectory saved to {trajectory_output_dirpath}")

    print(f"total simulation step time: {sim_step_time:.3f} seconds")
    print(f"simulation steps per second: {num_steps / sim_step_time:.1f}")
    print(f"total policy step time: {policy_step_time:.3f} seconds")
    print(f"policy steps per second: {num_steps / policy_step_time:.1f}")