"""
Tool definitions and implementations for the Insurance Agent
These tools allow the agent to search and retrieve insurance product information
"""
import json
from typing import Dict, List, Any
from pathlib import Path

# Load insurance data
DATA_PATH = Path(__file__).parent / "data" / "policies.json"

def load_insurance_data() -> Dict:
    """Load insurance data from JSON file"""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {DATA_PATH} not found. Using empty data.")
        return {
            "health_insurance": [],
            "term_insurance": [],
            "motor_insurance": [],
            "travel_insurance": []
        }

INSURANCE_DATA = load_insurance_data()

# Tool definitions for Claude API (following Anthropic's tool use format)
TOOLS = [
    {
        "name": "search_policies",
        "description": """Search for insurance policies based on category and optional filters.
Use this tool when you need to find insurance products that match the user's requirements.
Always search before making recommendations to ensure you have the latest product information.

Categories available:
- health_insurance: Individual, Family Floater, Super Top-up plans
- term_insurance: Pure term life insurance plans
- motor_insurance: Car and two-wheeler insurance
- travel_insurance: Domestic and international travel coverage""",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "The insurance category to search in",
                    "enum": ["health_insurance", "term_insurance", "motor_insurance", "travel_insurance"]
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters to narrow down results",
                    "properties": {
                        "max_premium": {
                            "type": "number",
                            "description": "Maximum annual premium budget in INR"
                        },
                        "min_cover": {
                            "type": "number",
                            "description": "Minimum coverage/sum insured needed in INR"
                        },
                        "policy_type": {
                            "type": "string",
                            "description": "Specific policy type (e.g., 'Individual', 'Family Floater', 'Comprehensive', 'Third Party')"
                        },
                        "age": {
                            "type": "number",
                            "description": "Age of the primary insured person"
                        },
                        "best_for": {
                            "type": "string",
                            "description": "Target user profile (e.g., 'young_professionals', 'families', 'senior_citizens')"
                        }
                    }
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "get_policy_details",
        "description": """Get comprehensive details about a specific insurance policy by its ID.
Use this after search_policies to get full information about a policy the user is interested in.
Returns all available information including features, exclusions, and terms.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_id": {
                    "type": "string",
                    "description": "The unique policy ID (e.g., 'health_001', 'term_002', 'motor_003')"
                }
            },
            "required": ["policy_id"]
        }
    },
    {
        "name": "compare_policies",
        "description": """Compare two or more insurance policies side by side.
Use this when the user wants to compare different options or is deciding between specific policies.
Provide 2-4 policy IDs for meaningful comparison.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of policy IDs to compare (2-4 policies recommended)",
                    "minItems": 2,
                    "maxItems": 4
                }
            },
            "required": ["policy_ids"]
        }
    }
]


def execute_tool(tool_name: str, tool_input: Dict) -> Any:
    """
    Execute a tool and return results
    
    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool
        
    Returns:
        Tool execution result (dict or list)
    """
    if tool_name == "search_policies":
        return search_policies(
            category=tool_input["category"],
            filters=tool_input.get("filters", {})
        )
    
    elif tool_name == "get_policy_details":
        return get_policy_details(tool_input["policy_id"])
    
    elif tool_name == "compare_policies":
        return compare_policies(tool_input["policy_ids"])
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def search_policies(category: str, filters: Dict = None) -> List[Dict]:
    """
    Search policies by category and optional filters
    
    Args:
        category: Insurance category (health_insurance, term_insurance, etc.)
        filters: Optional dict with filtering criteria
        
    Returns:
        List of matching policies (summary view)
    """
    if filters is None:
        filters = {}
    
    # Reload data to get any updates
    data = load_insurance_data()
    
    if category not in data:
        return {"error": f"Unknown category: {category}. Valid categories are: {list(data.keys())}"}
    
    results = data[category].copy()
    
    # Apply filters
    if "max_premium" in filters and filters["max_premium"]:
        max_premium = filters["max_premium"]
        results = [
            p for p in results 
            if p.get("premium_range", {}).get("max", float('inf')) <= max_premium
        ]
    
    if "min_cover" in filters and filters["min_cover"]:
        min_cover = filters["min_cover"]
        filtered = []
        for p in results:
            # Check sum_insured_options or cover_options
            cover_options = p.get("sum_insured_options", p.get("cover_options", [0]))
            if isinstance(cover_options, list) and max(cover_options) >= min_cover:
                filtered.append(p)
        results = filtered
    
    if "policy_type" in filters and filters["policy_type"]:
        policy_type = filters["policy_type"].lower()
        results = [
            p for p in results
            if policy_type in p.get("type", "").lower()
        ]
    
    if "age" in filters and filters["age"]:
        age = filters["age"]
        results = [
            p for p in results
            if p.get("age_range", {}).get("min", 0) <= age <= p.get("age_range", {}).get("max", 100)
        ]
    
    if "best_for" in filters and filters["best_for"]:
        target = filters["best_for"].lower()
        results = [
            p for p in results
            if any(target in bf.lower() for bf in p.get("best_for", []))
        ]
    
    # Return summary view (not full details) - limit to top 5
    summary_results = []
    for p in results[:5]:
        summary = {
            "id": p["id"],
            "name": p["name"],
            "provider": p["provider"],
            "type": p.get("type", "Standard"),
            "premium_range": p.get("premium_range", {}),
        }
        
        # Add category-specific fields
        if "claim_settlement_ratio" in p:
            summary["claim_settlement_ratio"] = f"{p['claim_settlement_ratio']*100:.1f}%"
        
        if "sum_insured_options" in p:
            summary["coverage_range"] = f"₹{min(p['sum_insured_options']):,} - ₹{max(p['sum_insured_options']):,}"
        elif "cover_options" in p:
            summary["coverage_range"] = f"₹{min(p['cover_options']):,} - ₹{max(p['cover_options']):,}"
        
        if "best_for" in p:
            summary["best_for"] = p["best_for"]
        
        if "network_hospitals" in p:
            summary["network_hospitals"] = f"{p['network_hospitals']:,}+"
        
        if "cashless_garages" in p:
            summary["cashless_garages"] = f"{p['cashless_garages']:,}+"
            
        summary_results.append(summary)
    
    if not summary_results:
        return {
            "message": "No policies found matching your criteria.",
            "suggestion": "Try broadening your search by adjusting filters."
        }
    
    return {
        "count": len(summary_results),
        "policies": summary_results
    }


def get_policy_details(policy_id: str) -> Dict:
    """
    Get full details of a specific policy
    
    Args:
        policy_id: The unique policy ID
        
    Returns:
        Complete policy details or error message
    """
    data = load_insurance_data()
    
    for category in data.values():
        for policy in category:
            if policy["id"] == policy_id:
                return policy
    
    return {
        "error": f"Policy not found: {policy_id}",
        "suggestion": "Use search_policies first to find valid policy IDs."
    }


def compare_policies(policy_ids: List[str]) -> Dict:
    """
    Get details of multiple policies for comparison
    
    Args:
        policy_ids: List of policy IDs to compare
        
    Returns:
        Dict with comparison data or error
    """
    if len(policy_ids) < 2:
        return {"error": "Please provide at least 2 policy IDs to compare."}
    
    if len(policy_ids) > 4:
        return {"error": "Please provide maximum 4 policies for meaningful comparison."}
    
    data = load_insurance_data()
    results = []
    not_found = []
    
    for pid in policy_ids:
        found = False
        for category in data.values():
            for policy in category:
                if policy["id"] == pid:
                    results.append(policy)
                    found = True
                    break
            if found:
                break
        if not found:
            not_found.append(pid)
    
    if not_found:
        return {
            "error": f"Some policies not found: {not_found}",
            "found_policies": results if results else None
        }
    
    # Create comparison summary
    comparison = {
        "policies_compared": len(results),
        "comparison": []
    }
    
    for policy in results:
        comp_item = {
            "id": policy["id"],
            "name": policy["name"],
            "provider": policy["provider"],
            "type": policy.get("type", "N/A"),
            "premium_range": policy.get("premium_range", {}),
            "key_features": policy.get("features", [])[:5],  # Top 5 features
        }
        
        if "claim_settlement_ratio" in policy:
            comp_item["claim_settlement_ratio"] = f"{policy['claim_settlement_ratio']*100:.1f}%"
        
        if "sum_insured_options" in policy:
            comp_item["coverage_options"] = policy["sum_insured_options"]
        elif "cover_options" in policy:
            comp_item["coverage_options"] = policy["cover_options"]
        
        if "network_hospitals" in policy:
            comp_item["network_hospitals"] = policy["network_hospitals"]
        
        if "waiting_period_days" in policy:
            comp_item["waiting_period_days"] = policy["waiting_period_days"]
        
        if "best_for" in policy:
            comp_item["best_for"] = policy["best_for"]
            
        comparison["comparison"].append(comp_item)
    
    return comparison


# For testing the tools directly
if __name__ == "__main__":
    print("Testing tools...")
    
    # Test search
    print("\n1. Search health insurance:")
    result = search_policies("health_insurance", {"age": 30, "max_premium": 20000})
    print(json.dumps(result, indent=2))
    
    # Test get details
    print("\n2. Get policy details:")
    result = get_policy_details("health_001")
    print(json.dumps(result, indent=2, default=str))
    
    # Test compare
    print("\n3. Compare policies:")
    result = compare_policies(["health_001", "health_002"])
    print(json.dumps(result, indent=2))
