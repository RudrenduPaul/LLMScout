"""
Programmatic / agent-native entry point.

    from llmscout import load_site, run_checks, select_checks, ALL_CHECKS

    ctx = load_site("https://example.com")
    results = run_checks(ALL_CHECKS, ctx)
    for r in results:
        print(r.status, r.name, r.message)

This is the Python port of the llmscout-cli npm package
(https://www.npmjs.com/package/llmscout-cli). Both distributions run the
same 21 technical-SEO/GEO checks; see
https://github.com/RudrenduPaul/LLMScout for the canonical documentation,
comparison table, and the original TypeScript source.
"""
from .checks import (
    ALL_CHECKS,
    GEO_CHECKS,
    TECHNICAL_CHECKS,
    ai_crawler_directives_check,
    canonical_check,
    content_extraction_check,
    faq_schema_check,
    heading_structure_check,
    image_alt_check,
    llms_txt_check,
    meta_description_check,
    robots_txt_check,
    sitemap_xml_check,
    structured_data_check,
    title_check,
)
from .config import CONFIG_FILENAME, LLMScoutConfig, default_config, load_config, select_checks
from .errors import LLMScoutError
from .fetch_utils import FetchedResource, assert_http_url, safe_fetch
from .fleet import FleetManifest, FleetManifestEntry, FleetSiteResult, load_fleet_manifest, run_fleet
from .format import (
    format_check_results_json,
    format_check_results_text,
    format_fleet_results_json,
    format_fleet_results_text,
    format_init_result_json,
    format_init_result_text,
)
from .init import InitResult, init_project
from .runner import has_failure, run_checks
from .site_resources import build_check_context, fetch_site_resources, load_site
from .types import Check, CheckContext, CheckResult, SiteResources

from importlib import metadata as _metadata

try:
    # Read the version from the installed package's own metadata instead of
    # hardcoding it here, so `llmscout --version` can never drift from the
    # published PyPI version again (it previously did: this string was left
    # at "0.3.3" while pyproject.toml moved on to 0.3.4). Works for both
    # regular and editable (`pip install -e`) installs.
    __version__ = _metadata.version("llmscout-cli")
except _metadata.PackageNotFoundError:  # pragma: no cover - running from source without an install
    __version__ = "0.0.0+unknown"

__all__ = [
    "__version__",
    # Types
    "Check",
    "CheckContext",
    "CheckResult",
    "SiteResources",
    "FetchedResource",
    "LLMScoutError",
    "LLMScoutConfig",
    "InitResult",
    "FleetManifest",
    "FleetManifestEntry",
    "FleetSiteResult",
    # Checks
    "ALL_CHECKS",
    "TECHNICAL_CHECKS",
    "GEO_CHECKS",
    "title_check",
    "meta_description_check",
    "canonical_check",
    "robots_txt_check",
    "sitemap_xml_check",
    "heading_structure_check",
    "image_alt_check",
    "structured_data_check",
    "llms_txt_check",
    "ai_crawler_directives_check",
    "faq_schema_check",
    "content_extraction_check",
    # Core functions
    "run_checks",
    "has_failure",
    "fetch_site_resources",
    "build_check_context",
    "load_site",
    "safe_fetch",
    "assert_http_url",
    "load_config",
    "default_config",
    "select_checks",
    "CONFIG_FILENAME",
    "init_project",
    "load_fleet_manifest",
    "run_fleet",
    "format_check_results_text",
    "format_check_results_json",
    "format_fleet_results_text",
    "format_fleet_results_json",
    "format_init_result_text",
    "format_init_result_json",
]
