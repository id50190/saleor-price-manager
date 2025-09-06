#!/usr/bin/env python3
"""
Utility to compare OpenAPI specifications and check for differences.

Usage:
    python scripts/compare-api-specs.py
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any

def load_json_spec(file_path: Path) -> Dict[str, Any]:
    """Load OpenAPI spec from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_yaml_spec(file_path: Path) -> Dict[str, Any]:
    """Load OpenAPI spec from YAML file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def extract_endpoints(spec: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Extract endpoint information from OpenAPI spec"""
    endpoints = {}
    paths = spec.get('paths', {})
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                key = f"{method.upper()} {path}"
                endpoints[key] = {
                    'summary': details.get('summary', 'No summary'),
                    'description': details.get('description', 'No description')[:100],
                    'tags': ', '.join(details.get('tags', [])),
                    'auth_required': 'Yes' if details.get('security') else 'No'
                }
    
    return endpoints

def compare_specs():
    """Compare different API specifications"""
    base_dir = Path('docs/api')
    
    # Load specifications
    try:
        fastapi_spec = load_json_spec(base_dir / 'updated-openapi.json')
        manual_spec = load_yaml_spec(base_dir / 'saleor-price-manager.yaml')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure to generate updated OpenAPI specs first:")
        print("curl http://localhost:8000/api/v1/openapi.json > docs/api/updated-openapi.json")
        sys.exit(1)
    
    # Extract endpoints
    fastapi_endpoints = extract_endpoints(fastapi_spec)
    manual_endpoints = extract_endpoints(manual_spec)
    
    print("🔍 OpenAPI Specification Comparison\n")
    
    # Compare basic info
    print("📋 Basic Information:")
    print("FastAPI Generated:")
    print(f"  Title: {fastapi_spec['info']['title']}")
    print(f"  Version: {fastapi_spec['info']['version']}")
    print(f"  Description: {fastapi_spec['info']['description'][:100]}...")
    
    print("\nManual YAML Spec:")
    print(f"  Title: {manual_spec['info']['title']}")
    print(f"  Version: {manual_spec['info']['version']}")
    print(f"  Description: {manual_spec['info']['description'][:100]}...")
    
    # Compare endpoints
    print(f"\n🛣️  Endpoints Comparison:")
    print(f"FastAPI Generated: {len(fastapi_endpoints)} endpoints")
    print(f"Manual YAML Spec: {len(manual_endpoints)} endpoints\n")
    
    all_endpoints = set(fastapi_endpoints.keys()) | set(manual_endpoints.keys())
    
    for endpoint in sorted(all_endpoints):
        in_fastapi = endpoint in fastapi_endpoints
        in_manual = endpoint in manual_endpoints
        
        if in_fastapi and in_manual:
            status = "✅ Both"
        elif in_fastapi:
            status = "⚠️  FastAPI only"
        else:
            status = "📝 Manual only"
        
        print(f"{endpoint:<35} - {status}")
    
    print(f"\n📊 Coverage Summary:")
    both = len(set(fastapi_endpoints.keys()) & set(manual_endpoints.keys()))
    fastapi_only = len(set(fastapi_endpoints.keys()) - set(manual_endpoints.keys()))
    manual_only = len(set(manual_endpoints.keys()) - set(fastapi_endpoints.keys()))
    
    print(f"  ✅ Documented in both: {both}")
    print(f"  ⚠️  FastAPI only: {fastapi_only}")
    print(f"  📝 Manual only: {manual_only}")
    
    if both > 0:
        coverage = (both / len(all_endpoints)) * 100
        print(f"  📈 Coverage: {coverage:.1f}%")

if __name__ == '__main__':
    compare_specs()
