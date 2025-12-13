import subprocess
import os
import shutil
import argparse
import platform

def clone_repo(repo_url, ref, repo_dirname):    
    shutil.rmtree(repo_dirname, ignore_errors=True)
    cmd = [
        "git", "clone",
        "--no-checkout",
        repo_url,
        repo_dirname
    ]
    subprocess.run(cmd, check=True)

    cmd = [
        "git", "-C", repo_dirname,
        "checkout", ref
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--src-ref", default="main")
    arg_parser.add_argument("--build-ref", default="build")
    arg_parser.add_argument("--repo-dirname", default="algovivo.repo")
    arg_parser.add_argument("--system", action="store_true")
    args = arg_parser.parse_args()

    algovivo_src_ref = args.src_ref
    algovivo_build_ref = args.build_ref

    algovivo_repo_url = "https://github.com/juniorrojas/algovivo.git"

    algovivo_repo_dirname = args.repo_dirname
    clone_repo(algovivo_repo_url, algovivo_src_ref, algovivo_repo_dirname)

    # clone build branch to tmp directory and move build directory
    tmp_build_dirname = "algovivo.build.tmp"
    clone_repo(algovivo_repo_url, algovivo_build_ref, tmp_build_dirname)

    build_target = os.path.join(algovivo_repo_dirname, "build")
    shutil.rmtree(build_target, ignore_errors=True)
    shutil.move(os.path.join(tmp_build_dirname, "build"), build_target)

    shutil.rmtree(tmp_build_dirname, ignore_errors=True)

    cmd = [
        "uv", "pip", "install",
    ]

    if args.system:
        cmd.append("--system")
    
    cmd.extend([
        "-e",
        os.path.join(algovivo_repo_dirname, "utils", "py")
    ])
    subprocess.run(cmd, check=True)

    algovivo_native_lib_filename = None

    m = platform.machine().lower()
    if m in ("aarch64", "arm64"):
        print("detected arm64 architecture")
        algovivo_native_lib_filename = os.path.join(
            algovivo_repo_dirname, "build", "native", "algovivo.arm64.so"
        )
    elif m in ("x86_64", "amd64"):
        print("detected amd64 architecture")
        algovivo_native_lib_filename = os.path.join(
            algovivo_repo_dirname, "build", "native", "algovivo.amd64.so"
        )
    else:
        raise RuntimeError("could not infer algovivo lib filename")

    print(f"found algovivo lib: {algovivo_native_lib_filename}")

    # create symlink in build/native directory
    symlink_path = os.path.join(algovivo_repo_dirname, "build", "native", "algovivo.so")
    if os.path.islink(symlink_path) or os.path.exists(symlink_path):
        os.remove(symlink_path)

    # use relative symlink since both files are in the same directory
    target_filename = os.path.basename(algovivo_native_lib_filename)
    os.symlink(target_filename, symlink_path)
    print(f"created symlink: {symlink_path} -> {target_filename}")