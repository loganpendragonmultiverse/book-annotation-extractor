# Changelog

## 1.2.1 - 2026-10-20

- Reject malformed typed annotation fields without fabricating text.
- Include complete boundary dates in date-filtered exports and reject invalid bounds.
- Escape supplied Markdown markup and create report files exclusively.

## 1.2.0 - 2026-10-16

- Added an English Kindle My Clippings adapter for title, metadata, location, date, multiline highlights, notes and bookmarks, with numbered malformed-block errors.
- Fixed filtering before deduplication so ineligible earlier records cannot hide eligible annotations. Preserved JSON, CSV and legacy line adapters.

## 1.1.0 - 2026-07-27

- Added Kindle text/HTML, Kobo CSV, and generic CSV import adapters.
- Added provenance, normalized deduplication, duplicate review, and work/platform/date/kind filters.
- Added grouped Markdown and portable CSV exports while preserving local-only operation.

## 1.0.0 - 2026-07-26

- Released the first complete Book Annotation Extractor command-line workflow.
- Added deterministic reporting, representative examples, cross-platform tests, and explicit limitations.
