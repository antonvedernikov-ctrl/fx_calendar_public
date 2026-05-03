# fx_calendar_public

Automated public mirror of EA-consumable calendar artifacts from the private
[`fx_research`](https://github.com/antonvedernikov-ctrl/fx_research) pipeline.

This repo exists so that a MetaTrader 5 EA can `WebRequest` against a
**public, unauthenticated** GitHub Pages URL without needing a PAT.

## Published artifacts

| Path | Description |
|---|---|
| `calendar/events.parquet` | Merged FF + MQL5 economic calendar (historic + 60-day forward) |
| `calendar/holidays.parquet` | Consolidated Tier 1 + Tier 2 bank holidays |
| `calendar/metadata.json` | Roll-up metadata (row counts, coverage, staleness check) |
| `features/seasonality_daily.parquet` | Deterministic daily seasonality features |

## Pages URL

```
https://antonvedernikov-ctrl.github.io/fx_calendar_public/calendar/events.parquet
https://antonvedernikov-ctrl.github.io/fx_calendar_public/calendar/holidays.parquet
https://antonvedernikov-ctrl.github.io/fx_calendar_public/calendar/metadata.json
https://antonvedernikov-ctrl.github.io/fx_calendar_public/features/seasonality_daily.parquet
```

## Refresh cadence

Updated daily at ~23:15 UTC by the `refresh-calendar` workflow in the private
`fx_research` repo. A mirror step pushes the four files here and triggers a
Pages deploy.

## Staleness check

```bash
curl -sf https://antonvedernikov-ctrl.github.io/fx_calendar_public/calendar/metadata.json \
  | jq '.generated_at_utc'
```

Compare `generated_at_utc` to the current time; if older than 36 hours the
data is likely stale.

## License

The underlying data originates from publicly available sources
(ForexFactory, MQL5 economic calendar, python-holidays). This mirror
contains only the processed calendar artifacts, not the research code.
