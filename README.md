
<div align="right">
  <details>
    <summary >🌐 Language</summary>
    <div>
      <div align="right">
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=en">English</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=zh-CN">简体中文</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=zh-TW">繁體中文</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=ja">日本語</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=ko">한국어</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=hi">हिन्दी</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=th">ไทย</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=fr">Français</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=de">Deutsch</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=es">Español</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=it">Itapano</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=ru">Русский</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=pt">Português</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=nl">Nederlands</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=pl">Polski</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=ar">العربية</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=fa">فارسی</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=tr">Türkçe</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=vi">Tiếng Việt</a></p>
        <p><a href="https://openaitx.github.io/view.html?user=juniorrojas&project=morphology-adaptive&lang=id">Bahasa Indonesia</a></p>
      </div>
    </div>
  </details>
</div>

# morphology-adaptive

This repository demonstrates how a single locomotion controller can work with different shapes (biped and quadruped). It uses an attention mechanism to handle an arbitrary number of inputs, and the same module is shared across all muscles to support an arbitrary number of outputs.

**More details will be available in an upcoming paper.**

<a href="https://www.youtube.com/watch?v=gmgyFIJz9ZY">
  <img src="media/anim.gif">
</a>

View animation in higher quality [here](https://www.youtube.com/watch?v=gmgyFIJz9ZY).

For simulation, this repository uses [Algovivo](https://github.com/juniorrojas/algovivo), originally built for the browser using WebAssembly, but here a native build is used to enable PyTorch integration.

The workflow [`trajectory-attn.yml`](.github/workflows/trajectory-attn.yml) runs the controller on both morphologies and generates a video. If you have your own copy or fork of this repository, you can [run the workflow from the GitHub Actions UI](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/manually-running-a-workflow), no local installation needed. Once it completes, the video will be saved as a workflow artifact and can be downloaded from the workflow run page.