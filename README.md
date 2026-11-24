# Census Lens

[Open Census Lens](https://coolcode.ca/census-lens/)

<!-- coolcode:guide -->
Search Langley and switch between the district municipality and the city. The 2021 Census reports 132,603 residents in the district municipality and 28,963 in the city. Compare either one with Halifax Regional Municipality, then select median age or the tenant share.
<!-- /coolcode:guide -->

Compare any two geographies across the country. The national release includes the country, provinces, territories, census subdivisions, metropolitan areas, agglomerations and their published parts. Search multiple words or a geographic identifier. A place’s full census designation and DGUID appear together in the picker. The source-profile links open the original geography and all census characteristics. You can choose a featured indicator, filter the table by topic, and export the comparison including source symbols.

The 16 indicators include population and growth from 2016 to 2021, housing counts, density, median age, average household size, household income, tenure, rented shelter costs, official-language knowledge, immigration and education. Income values refer to 2020. Percentages use the published rate for the characteristic, including its specific denominator. Education covers people 15 and older in private households. The difference uses percentage points when the featured indicator is a percentage. Geographic parts, metropolitan areas and municipal boundaries can overlap.

The importer selects Statistics Canada characteristic identifiers from the 2021 Census Profile bulk files 001, 002 and 016–028. It retains the reported total count or rate cell, suppression symbols, geographic quality flag and short/long-form total non-response rates. Missing cells stay blank in the CSV export. Census counts can reflect rounding or incomplete enumeration. Consult the linked profile for the full notes on a geography. The source check runs quarterly.

[Statistics Canada Census Profile, 2021 Census of Population, catalogue 98-316-X2021001](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm?Lang=E) · [Bulk download files](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?Lang=E) · [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/reference/licence).

## Refresh and development

The committed edition builds offline. The scheduled workflow downloads the official archives, validates the edition, runs the browser checks, then commits the refreshed snapshot and deploys it. Source retrieval dates are separate from the observation periods. A failed refresh leaves the last published edition available.

Run `python3 scripts/refresh.py` to retrieve current source files, `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests` and `python3 scripts/build.py` to check and build. Preview using `python3 -m http.server --directory dist`. The interactive browser check is `python3 tests/browser_smoke.py` after installing the test-only Playwright dependency and its Chromium browser.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. The independent scheduler on our Linux server triggers overdue refreshes and checks published freshness; its code and current target list live in [the hub repository](https://github.com/jsdyer/jsdyer.github.io/tree/main/services/refresh-watchdog). The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->

Source requests are bounded by time and size. If the primary HTTPS client has a transport error or a 403/429/server response, the collector tries the same public URL with curl (installed on GitHub runners; optional locally). TLS verification remains enabled. Both clients must obtain a valid response and the existing data validation must pass before a successful check is recorded. If both fail, the previous publication keeps its original dates.

A change to the collector, its browser regression check or its Pages workflow triggers a live refresh before publication. Ordinary UI and data-only commits still build from retained data. Scheduled and manual refresh controls are unchanged.

The online collection job uses the standard `macos-15` GitHub runner because the public source returned HTTP 403 to both HTTPS clients on the Linux runner. The source URL, validation and collection schedule are unchanged.
