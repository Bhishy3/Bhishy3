# Bhishan Charitra (Bhishy3)

<p align="center">
  <img width="120" src="https://github.com/Bhishy3.png" alt="avatar" />
</p>

A Mechatronics student working across embedded systems, mechanical design, and software. I build the hardware and the interfaces that control it.

[![Python](https://img.shields.io/badge/Python-0a2e18?style=for-the-badge&logo=python&logoColor=3ecf74)](https://github.com/Bhishy3?tab=repositories&language=python)
[![Website](https://img.shields.io/badge/Portfolio-0a2e18?style=flat-square&logo=readme&logoColor=3ecf74)](https://github.com/Bhishy3)

---

## Quick overview

- Location: Melbourne, AU
- Focus: RTOS & real-time motor control, SwiftUI dashboards, mechatronics + on-device ML
- Current: Building **Triad**

---

## Generated profile stats

This repository contains a small generator (actions.py) that fetches your public GitHub data and writes a visual summary to `assets/stats.svg`.

![Profile stats](assets/stats.svg)

If the image doesn't show yet, run the generator locally or let the included GitHub Actions workflow generate it on the next scheduled run.

---

## How it works

- actions.py uses the GitHub REST and GraphQL APIs to gather contributions, languages, stars, followers and repository stats and then writes `assets/stats.svg`.
- A GitHub Actions workflow (.github/workflows/generate-stats.yml) is included and configured to run on a schedule and on-demand (workflow_dispatch). The action runs actions.py and commits `assets/stats.svg` back to the repository so the README always shows an up-to-date image.

### Run locally

1. Ensure you have Python 3.8+ installed.
2. Export a token with read access to your account data (optional for public data but recommended for higher rate limits):

```bash
export GH_TOKEN=ghp_xxx
# or use GITHUB_TOKEN in CI
```

3. Run:

```bash
python actions.py
```

The script will write `assets/stats.svg`.

---

## Files of interest

- `actions.py` — generator script (already in this repo). It will also read `GITHUB_TOKEN` when run inside GitHub Actions.
- `.github/workflows/generate-stats.yml` — workflow that runs the generator and commits the result.

---

## Contributing

If you'd like changes to the layout or additional data shown in the generated SVG, open an issue or submit a PR with a mockup of the desired change.

---

## License

This repo is available under the MIT License.
