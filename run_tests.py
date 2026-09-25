"""
Test Runner Script for Phani AI Automated Test Suite.
"""

import sys
from tests.test_router import (
    test_typo_correction, test_weather_routing, test_cricket_routing,
    test_crypto_routing, test_currency_routing
)
from tests.test_services import (
    test_weather_service, test_crypto_service, test_currency_service,
    test_wikipedia_service
)
from tests.test_database import test_conversation_logging, test_analytics_summary
from tests.test_auth import test_password_hashing, test_user_authentication, test_rbac_authorization
from tests.test_orchestrator import test_multi_intent_detection, test_orchestrator_execution
from tests.test_data_analysis import test_data_analysis_engine
from tests.test_cricket import (
    test_cricket_routing_variations, test_cricket_context_retention,
    test_cricket_service_live_fetch, test_orchestrator_cricket_execution
)
from tests.test_universal_topic import (
    test_natural_language_topic_parsing, test_dynamic_explanation_diverse_domains,
    test_dynamic_quiz_generation
)
from tests.test_live_timestamps import (
    test_live_data_timestamps, test_universal_currency_converter,
    test_currency_natural_language_routing, test_orchestrator_currency_live_response
)
from tests.test_multi_source_research import (
    test_query_decomposition, test_source_deduplication_and_ranking,
    test_typo_normalization_and_topic_extraction, test_research_routing_and_synthesis,
    test_followup_context_resolution
)
from tests.test_movie_and_maps import (
    test_movie_service_schema_safety, test_maps_service_query_parsing,
    test_maps_url_generation, test_maps_full_location_service, test_maps_context_followup
)
from tests.test_movie_search_and_no_dictionary import (
    test_general_ai_routing_no_dictionary, test_specialized_services_routing_boundaries,
    test_movie_typo_abbreviation_and_year_filtering, test_movie_nonexistent_and_error_handling,
    test_movie_followup_context
)
from tests.test_natural_topic_input import (
    test_topic_only_queries_and_clean_entities,
    test_explicit_instructions_override_defaults,
    test_contextual_followups,
    test_no_generic_filler_in_response
)


def run_all_tests():
    print("=" * 60)
    print("🚀 PHANI AI — AUTOMATED TEST SUITE RUNNER")
    print("=" * 60)

    tests = [
        ("Natural Topic Only Queries & Clean Entities", test_topic_only_queries_and_clean_entities),
        ("Explicit Instruction Parameter Overrides", test_explicit_instructions_override_defaults),
        ("Contextual Conversational Topic Followups", test_contextual_followups),
        ("No Generic Filler in Responses", test_no_generic_filler_in_response),
        ("General AI Routing & Zero Dictionary Routing", test_general_ai_routing_no_dictionary),
        ("Specialized Services Intent Routing Boundaries", test_specialized_services_routing_boundaries),
        ("Movie Typo, Abbreviation & Year Filtering", test_movie_typo_abbreviation_and_year_filtering),
        ("Movie Non-existent Match & Error Handling", test_movie_nonexistent_and_error_handling),
        ("Movie Follow-up Context Retention", test_movie_followup_context),
        ("Movie Service Schema Safety & KeyError Prevention", test_movie_service_schema_safety),
        ("Maps Query & Travel Mode Parsing", test_maps_service_query_parsing),
        ("Google Maps Search & Direction URL Building", test_maps_url_generation),
        ("Maps Full Location Service Execution", test_maps_full_location_service),
        ("Maps Context Retention Across Follow-ups", test_maps_context_followup),
        ("Multi-Source Query Decomposition", test_query_decomposition),
        ("Source Deduplication & Authority Ranking", test_source_deduplication_and_ranking),
        ("Typo Normalization & Topic/Intent Extraction", test_typo_normalization_and_topic_extraction),
        ("Multi-Source Research Routing & Citation Synthesis", test_research_routing_and_synthesis),
        ("Follow-up Context & Pronoun Resolution", test_followup_context_resolution),
        ("Live Data Timestamp Requirements", test_live_data_timestamps),
        ("Universal Forex Currency Converter", test_universal_currency_converter),
        ("Currency Natural Language Routing", test_currency_natural_language_routing),
        ("Orchestrator Currency Live Response", test_orchestrator_currency_live_response),
        ("Natural Language Topic Parsing", test_natural_language_topic_parsing),
        ("Universal Explanation Across Diverse Domains", test_dynamic_explanation_diverse_domains),
        ("Dynamic Quiz Generation", test_dynamic_quiz_generation),
        ("Password Hashing & PBKDF2", test_password_hashing),
        ("User Authentication & Registration", test_user_authentication),
        ("RBAC & Data Isolation Authorization", test_rbac_authorization),
        ("Multi-Intent Detection", test_multi_intent_detection),
        ("Orchestrator Execution", test_orchestrator_execution),
        ("Data Analysis Engine", test_data_analysis_engine),
        ("Live Cricket Routing Variations", test_cricket_routing_variations),
        ("Live Cricket Context Retention", test_cricket_context_retention),
        ("Live Cricket RSS Service Fetch", test_cricket_service_live_fetch),
        ("Orchestrator Cricket Execution", test_orchestrator_cricket_execution),
        ("Typo Correction", test_typo_correction),
        ("Weather Query Routing", test_weather_routing),
        ("Cricket Query Routing", test_cricket_routing),
        ("Crypto Query Routing", test_crypto_routing),
        ("Currency Query Routing", test_currency_routing),
        ("Weather Service", test_weather_service),
        ("Crypto Service", test_crypto_service),
        ("Currency Service", test_currency_service),
        ("Wikipedia Service", test_wikipedia_service),
        ("Database Conversation Logging", test_conversation_logging),
        ("Database Analytics Summary", test_analytics_summary)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ PASSED: {name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {name} — {e}")
            failed += 1

    print("=" * 60)
    print(f"TOTAL: {passed + failed} | PASSED: {passed} | FAILED: {failed}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
