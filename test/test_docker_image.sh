#!/usr/bin/env bash
#
# usage: test/test_docker_image.sh <image> [output-dirname]
#
# outputs (trajectories, frames and, if ffmpeg is available, videos) are written
# to output-dirname, or to a temporary directory if not provided

set -euo pipefail

image="${1:?usage: $0 <image> [output-dirname]}"
output_dirname="${2:-$(mktemp -d)}"
mkdir -p "$output_dirname"
output_dirname="$(cd "$output_dirname" && pwd)"

repo_dirname="$(cd "$(dirname "$0")/.." && pwd)"

steps=20
frame_size=100

echo "image: $image"
echo "output dirname: $output_dirname"

# pytest is not part of the image, so it is installed in a throwaway container
echo "running pytest"
pytest_requirement=$(sed -n '/^pytest/p' "$repo_dirname/requirements.txt")
docker run --rm \
  -v "$repo_dirname/test":/tests:ro \
  "$image" \
  sh -c "uv pip install --system -q '$pytest_requirement' && python -m pytest -p no:cacheprovider /tests"

run() {
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "$output_dirname":/workspace \
    -w /workspace \
    "$image" \
    "$@"
}

echo "checking algovivo.so architecture"
expected_arch=$(docker image inspect --format '{{.Architecture}}' "$image")
actual_arch=$(docker run --rm "$image" readlink /morphology-adaptive/algovivo.repo/build/native/algovivo.so | sed 's/algovivo\.\(.*\)\.so/\1/')
if [ "$actual_arch" != "$expected_arch" ]; then
  echo "error: algovivo.so targets '$actual_arch', expected '$expected_arch'"
  exit 1
fi
echo "algovivo.so targets $expected_arch"

for agent in biped quadruped; do
  echo "generating $agent trajectory"
  run python /morphology-adaptive/scripts/generate_trajectory_with_attn_policy.py \
    --agent /morphology-adaptive/data/agents/$agent \
    --policy /morphology-adaptive/data/policies/attn \
    --steps $steps \
    -o $agent.trajectory.out

  test -f "$output_dirname/$agent.trajectory.out/mesh.json"
  num_step_files=$(find "$output_dirname/$agent.trajectory.out/steps" -name '*.json' | wc -l | tr -d ' ')
  if [ "$num_step_files" != "$steps" ]; then
    echo "error: expected $steps step files, found $num_step_files"
    exit 1
  fi

  echo "rendering $agent frames"
  run node /morphology-adaptive/algovivo.repo/utils/trajectory/renderTrajectory.js \
    --mesh ./$agent.trajectory.out/mesh.json \
    --steps ./$agent.trajectory.out/steps \
    --width $frame_size \
    --height $frame_size \
    -o $agent.frames.out

  num_frames=$(find "$output_dirname/$agent.frames.out" -name '*.png' | wc -l | tr -d ' ')
  if [ "$num_frames" -eq 0 ]; then
    echo "error: no frames rendered"
    exit 1
  fi
  echo "rendered $num_frames frames"

  if command -v ffmpeg > /dev/null; then
    echo "making $agent video"
    ffmpeg -y -loglevel error \
      -framerate 30 \
      -i "$output_dirname/$agent.frames.out/%d.png" \
      -c:v libx264 \
      -profile:v high \
      -crf 20 \
      -pix_fmt yuv420p \
      "$output_dirname/$agent.video.out.mp4"
    test -s "$output_dirname/$agent.video.out.mp4"
  else
    echo "ffmpeg not found, skipping video"
  fi
done

echo "all docker image tests passed"
