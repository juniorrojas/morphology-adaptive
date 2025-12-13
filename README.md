# morphology-adaptive muscle-driven locomotion via attention mechanisms

<p>
  <a href="https://github.com/juniorrojas/morphology-adaptive/actions/workflows/test.yml">
    <img src="https://github.com/juniorrojas/morphology-adaptive/actions/workflows/test.yml/badge.svg" alt="Test">
  </a>
  <a href="https://deepwiki.com/juniorrojas/morphology-adaptive">
    <img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki">
  </a>
</p>

This repository demonstrates how a single locomotion controller can work with different shapes (biped and quadruped). It uses an attention mechanism to handle an arbitrary number of inputs, and the same module is shared across all muscles to support an arbitrary number of outputs.

More details in [this paper](https://juniorrojas.com/papers/2025-morphology-adaptive.pdf).

<a href="https://www.youtube.com/watch?v=gmgyFIJz9ZY">
  <img src="media/anim.gif">
</a>

View animation in higher quality [here](https://www.youtube.com/watch?v=gmgyFIJz9ZY).

For simulation, this repository uses [Algovivo](https://github.com/juniorrojas/algovivo), originally built for the browser using WebAssembly, but here a native build is used to enable PyTorch integration.

## run on GitHub Actions

The workflow [`trajectory-attn.yml`](.github/workflows/trajectory-attn.yml) runs the controller on both morphologies and generates a video. If you have your own copy or fork of this repository, you can [run the workflow from the GitHub Actions UI](https://docs.github.com/en/actions/how-tos/managing-workflow-runs-and-deployments/managing-workflow-runs/manually-running-a-workflow#running-a-workflow), no local installation needed. Once it completes, the video will be saved as a workflow artifact and can be downloaded from the workflow run page.

## run locally

Pull the Docker image:

```sh
docker pull ghcr.io/juniorrojas/morphology-adaptive/bundle:latest
```

Generate trajectory (use `biped` or `quadruped`):

```sh
docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd):/workspace \
  -w /workspace \
  ghcr.io/juniorrojas/morphology-adaptive/bundle:latest \
  python /morphology-adaptive/scripts/generate_trajectory_with_attn_policy.py \
  --agent /morphology-adaptive/data/agents/biped \
  --policy /morphology-adaptive/data/policies/attn \
  --steps 200 \
  -o trajectory.out
```

Render frames:

```sh
docker run --rm \
  --user $(id -u):$(id -g) \
  -e HOME=/tmp \
  -v $(pwd):/workspace \
  -w /workspace \
  ghcr.io/juniorrojas/morphology-adaptive/bundle:latest \
  node /morphology-adaptive/algovivo.repo/utils/trajectory/renderTrajectory.js \
  --mesh ./trajectory.out/mesh.json \
  --steps ./trajectory.out/steps \
  --width 300 \
  --height 300 \
  -o frames.out
```

Make video:

```sh
ffmpeg -y \
  -framerate 30 \
  -i frames.out/%d.png \
  -c:v libx264 \
  -profile:v high \
  -crf 20 \
  -pix_fmt yuv420p \
  video.out.mp4
```

## citation

```bibtex
@inproceedings{10.1145/3712255.3734277,
  author = {Rojas, Junior},
  title = {Morphology-Adaptive Muscle-Driven Locomotion via Attention Mechanisms},
  year = {2025},
  isbn = {9798400714641},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  url = {https://doi.org/10.1145/3712255.3734277},
  doi = {10.1145/3712255.3734277},
  booktitle = {Proceedings of the Genetic and Evolutionary Computation Conference Companion},
  pages = {2138–2142},
  numpages = {5},
  keywords = {neural networks, attention mechanisms, virtual creatures},
  location = {NH Malaga Hotel, Malaga, Spain},
  series = {GECCO '25 Companion}
}
```