# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Created `docs/AGENT_ROLES.md` to define agent roles.
- Established the "Librarian" (Documentation Agent) role.
- Organized documentation structure in `docs/`.

### Changed
- Moved `README.md` from `docs/` to project root for better visibility.
### Fixed
- **Google Login**: Implemented a hardcoded fallback for `GOOGLE_CLIENT_ID` in `core/settings.py` to resolve the `invalid_client` (401) error on Azure deployments where environment variables were failing.
- **Listing Companies**: Fixed a `TemplateSyntaxError` (500) in `empresarios/templates/listar_empresas.html` caused by a malformed/split `{% endif %}` tag.
