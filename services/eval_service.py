"""
Benchmark Quality Control Evaluation System for Phani AI.
Evaluates accuracy, relevance, intent routing, typo tolerance, response latency, and failure rate across standard test suites.
Restricted exclusively to authorized administrators.
"""

import time
import logging
from typing import Dict, Any, List
from services.router_service import router_service
from services.orchestrator import orchestrator
from utils.typo_tolerance import correct_typos

logger = logging.getLogger("PhaniAI.EvalService")

BENCHMARK_SUITES = [
    {
        "domain": "Typo Handling",
        "query": "wether in Hyderabad",
        "expected_intent": "WEATHER",
        "expected_entity": "location",
        "expected_entity_val": "Hyderabad"
    },
    {
        "domain": "Sports API Routing",
        "query": "criket score today",
        "expected_intent": "CRICKET",
        "expected_entity": None,
        "expected_entity_val": None
    },
    {
        "domain": "Crypto Market Routing",
        "query": "bitcion price",
        "expected_intent": "CRYPTO",
        "expected_entity": "asset",
        "expected_entity_val": "Bitcoin"
    },
    {
        "domain": "Forex Currency Routing",
        "query": "Convert 500 dollars to rupees",
        "expected_intent": "CURRENCY",
        "expected_entity": "amount",
        "expected_entity_val": 500.0
    },
    {
        "domain": "General Knowledge AI",
        "query": "Explain quantum computing briefly",
        "expected_intent": "GENERAL_AI",
        "expected_entity": None,
        "expected_entity_val": None
    }
]


class BenchmarkEvalService:
    def run_benchmark_suite(self) -> Dict[str, Any]:
        """Run standard benchmark test suite and return quality metrics."""
        total_tests = len(BENCHMARK_SUITES)
        passed_intents = 0
        passed_entities = 0
        total_latency = 0.0
        failures = 0
        results_list = []

        for item in BENCHMARK_SUITES:
            start = time.time()
            try:
                res = orchestrator.process_request(item["query"])
                latency = round((time.time() - start) * 1000, 2)
                total_latency += latency

                intent_pass = res["primary_intent"] == item["expected_intent"]
                if intent_pass:
                    passed_intents += 1

                entity_pass = True
                if item["expected_entity"]:
                    entity_val = res["entities"].get(item["expected_entity"])
                    entity_pass = entity_val == item["expected_entity_val"]

                if entity_pass:
                    passed_entities += 1

                status = "PASSED" if (intent_pass and entity_pass) else "FAILED"

                results_list.append({
                    "domain": item["domain"],
                    "query": item["query"],
                    "detected_intent": res["primary_intent"],
                    "expected_intent": item["expected_intent"],
                    "intent_pass": intent_pass,
                    "entity_pass": entity_pass,
                    "latency_ms": latency,
                    "status": status
                })
            except Exception as e:
                logger.error(f"Benchmark test failure for '{item['query']}': {e}")
                failures += 1
                results_list.append({
                    "domain": item["domain"],
                    "query": item["query"],
                    "status": "ERROR",
                    "latency_ms": 0.0,
                    "error": str(e)
                })

        avg_latency = round(total_latency / max(total_tests, 1), 2)
        intent_accuracy = round((passed_intents / total_tests) * 100, 1)
        entity_accuracy = round((passed_entities / total_tests) * 100, 1)

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_benchmark_tests": total_tests,
            "passed_tests": passed_intents,
            "failed_tests": failures + (total_tests - passed_intents),
            "intent_accuracy_pct": intent_accuracy,
            "entity_accuracy_pct": entity_accuracy,
            "avg_response_latency_ms": avg_latency,
            "failure_rate_pct": round((failures / total_tests) * 100, 1),
            "detailed_results": results_list
        }


eval_service = BenchmarkEvalService()
