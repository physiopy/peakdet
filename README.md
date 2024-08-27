<!--(https://raw.githubusercontent.com/physiopy/phys2bids/master/docs/_static/phys2bids_card.jpg)-->
<a name="readme"></a>
<!-- <img alt="Phys2BIDS" src="https://github.com/physiopy/phys2bids/blob/master/docs/_static/phys2bids_logo1280×640.png" height="150"> -->

peakdet: A toolbox for physiological peak detection analyses
============================================================

[![Apache 2.0](https://img.shields.io/badge/license-Apache%202-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![Join the chat at Gitter: https://gitter.im/physiopy](https://badges.gitter.im/physiopy/phys2bids.svg)](https://gitter.im/physiopy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=body_badge)
[![codecov](https://codecov.io/gh/rmarkello/peakdet/branch/master/graph/badge.svg)](https://codecov.io/gh/rmarkello/peakdet)

[![TravisCI](https://travis-ci.org/rmarkello/peakdet.svg?branch=master)](https://travis-ci.org/rmarkello/peakdet)
[![See the documentation at: http://peakdet.readthedocs.io](https://readthedocs.org/projects/peakdet/badge/?version=latest)](http://peakdet.readthedocs.io/en/latest)

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-9-orange.svg?style=flat)](#contributors)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

This package is designed for use in the reproducible processing and analysis of
physiological data, like those collected from respiratory belts, pulse
photoplethysmography, or electrocardiogram (ECG/EKG) monitors.

## Overview

Physiological data are messy and prone to artifact (e.g., movement in
respiration and pulse, ectopic beats in ECG). Despite leaps and bounds in
recent algorithms for processing these data there still exists a need for
manual inspection to ensure such artifacts have been appropriately removed.
Because of this manual intervention step, understanding exactly what happened
to go from "raw" data to "analysis-ready" data can often be difficult or
impossible.

This toolbox, ``peakdet``, aims to provide a set of tools that will work with a
variety of input data to reproducibly generate manually-corrected, analysis-
ready physiological data. If you'd like more information about the package,
including how to install it and some example instructions on its use, check out
our `documentation <https://peakdet.readthedocs.io>`_!

## License Information

This codebase is licensed under the Apache License, Version 2.0. The full
license can be found in the `LICENSE <https://github.com/physiopy/peakdet/
blob/master/LICENSE>`_ file in the ``peakdet`` distribution. You may also
obtain a copy of the license at: http://www.apache.org/licenses/LICENSE-2.0.


## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="25%"><a href="https://github.com/emdupre"><img src="https://avatars3.githubusercontent.com/u/15017191?v=4?s=100" width="100px;" alt="Elizabeth DuPre"/><br /><sub><b>Elizabeth DuPre</b></sub></a><br /><a href="https://github.com/physiopy/peakdet/commits?author=emdupre" title="Code">💻</a> <a href="#infra-emdupre" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="25%"><a href="https://github.com/rmarkello"><img src="https://avatars0.githubusercontent.com/u/14265705?v=4?s=100" width="100px;" alt="Ross Markello"/><br /><sub><b>Ross Markello</b></sub></a><br /><a href="https://github.com/physiopy/peakdet/issues?q=author%3Armarkello" title="Bug reports">🐛</a> <a href="https://github.com/physiopy/peakdet/commits?author=rmarkello" title="Code">💻</a> <a href="https://github.com/physiopy/peakdet/commits?author=rmarkello" title="Documentation">📖</a> <a href="#ideas-rmarkello" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-rmarkello" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-rmarkello" title="Maintenance">🚧</a> <a href="#projectManagement-rmarkello" title="Project Management">📆</a> <a href="https://github.com/physiopy/peakdet/pulls?q=is%3Apr+reviewed-by%3Armarkello" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/physiopy/peakdet/commits?author=rmarkello" title="Tests">⚠️</a> <a href="#tutorial-rmarkello" title="Tutorials">✅</a></td>
      <td align="center" valign="top" width="25%"><a href="https://github.com/smoia"><img src="https://avatars.githubusercontent.com/u/35300580?v=4?s=100" width="100px;" alt="Stefano Moia"/><br /><sub><b>Stefano Moia</b></sub></a><br /><a href="https://github.com/physiopy/peakdet/pulls?q=is%3Apr+reviewed-by%3Asmoia" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/physiopy/peakdet/commits?author=smoia" title="Code">💻</a> <a href="#infra-smoia" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#projectManagement-smoia" title="Project Management">📆</a></td>
      <td align="center" valign="top" width="25%"><a href="https://github.com/tsalo"><img src="https://avatars.githubusercontent.com/u/8228902?v=4?s=100" width="100px;" alt="Taylor Salo"/><br /><sub><b>Taylor Salo</b></sub></a><br /><a href="#infra-tsalo" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="25%"><a href="https://github.com/mixue-t"><img src="https://avatars.githubusercontent.com/u/28149789?v=4?s=100" width="100px;" alt="Mi-Xue Tan"/><br /><sub><b>Mi-Xue Tan</b></sub></a><br /><a href="https://github.com/physiopy/peakdet/commits?author=mixue-t" title="Code">💻</a> <a href="#userTesting-mixue-t" title="User Testing">📓</a> <a href="#plugin-mixue-t" title="Plugin/utility libraries">🔌</a></td>
      <td align="center" valign="top" width="25%"><a href="https://github.com/eurunuela"><img src="https://avatars.githubusercontent.com/u/13706448?v=4?s=100" width="100px;" alt="Eneko Uruñuela"/><br /><sub><b>Eneko Uruñuela</b></sub></a><br /><a href="#infra-eurunuela" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="25%"><a href="https://github.com/xl624"><img src="https://avatars0.githubusercontent.com/u/25593301?v=4?s=100" width="100px;" alt="xl624"/><br /><sub><b>xl624</b></sub></a><br /><a href="https://github.com/physiopy/peakdet/commits?author=xl624" title="Code">💻</a></td>
      <td align="center" valign="top" width="25%"><a href="https://github.com/maestroque"><img src="https://avatars.githubusercontent.com/u/74024609?v=4?s=100" width="100px;" alt="George Kikas"/><br /><sub><b>George Kikas</b></sub></a><br /><a href="https://github.com/physiopy/peakdet/issues?q=author%3Amaestroque" title="Bug reports">🐛</a> <a href="https://github.com/physiopy/peakdet/commits?author=maestroque" title="Code">💻</a> <a href="#ideas-maestroque" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-maestroque" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/physiopy/peakdet/pulls?q=is%3Apr+reviewed-by%3Amaestroque" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/physiopy/peakdet/commits?author=maestroque" title="Tests">⚠️</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="25%"><a href="https://github.com/RayStick"><img src="https://avatars.githubusercontent.com/u/50215726?v=4?s=100" width="100px;" alt="Rachael Stickland"/><br /><sub><b>Rachael Stickland</b></sub></a><br /><a href="https://github.com/physiopy/peakdet/commits?author=RayStick" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
