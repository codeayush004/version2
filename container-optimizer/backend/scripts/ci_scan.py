import sys
import os
import requests
import json
import argparse

def scan_dockerfile(api_url, dockerfile_path, create_pr=False, repo_url=None, github_token=None):
    if not os.path.exists(dockerfile_path):
        print(f"Error: Dockerfile not found at {dockerfile_path}")
        sys.exit(1)

    with open(dockerfile_path, 'r') as f:
        content = f.read()

    print(f"Scanning Dockerfile: {dockerfile_path}...")
    
    try:
        response = requests.post(
            f"{api_url}/api/analyze-dockerfile",
            json={"content": content},
            timeout=60
        )
        response.raise_for_status()
        report = response.json()

        # Check for critical security warnings
        security_warnings = report.get("recommendation", {}).get("security_warnings", [])
        optimized_content = report.get("recommendation", {}).get("optimized_dockerfile")
        
        print("\n--- Scan Results ---")
        if security_warnings:
            print(f"Found {len(security_warnings)} security warnings:")
            for warning in security_warnings:
                print(f"  - {warning}")
        else:
            print("No security warnings found!")

        # Choice mechanism: Auto-PR
        if create_pr and optimized_content and (security_warnings or report.get("recommendation", {}).get("explanation")):
            if not repo_url or not github_token:
                print("Warning: Skipping Auto-PR (repo_url or github_token missing)")
            else:
                print("\nInitiating Auto-PR for optimization...")
                pr_payload = {
                    "url": repo_url,
                    "updates": [{"path": dockerfile_path, "content": optimized_content}],
                    "token": github_token,
                    "pr_title": "✨ [Optimizer] Improved Dockerfile for Performance & Security",
                    "commit_message": "Optimized Dockerfile via AI Container Optimizer CI"
                }
                pr_resp = requests.post(f"{api_url}/api/create-bulk-pr", json=pr_payload)
                if pr_resp.status_code == 200:
                    print(f"✅ Success! Pull Request created: {pr_resp.json().get('message')}")
                else:
                    print(f"❌ Failed to create PR: {pr_resp.text}")

        # Logic to fail the CI if critical issues are found
        if security_warnings:
            print("\nCI Status: FAILED (Security risks detected)")
            sys.exit(1)
        
        print("\nCI Status: PASSED")
        sys.exit(0)

    except Exception as e:
        print(f"Error communicating with Optimizer API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Container Optimizer CI Tool")
    parser.add_argument("--api-url", required=True, help="Base URL of the Container Optimizer API")
    parser.add_argument("--file", default="Dockerfile", help="Path to the Dockerfile to scan")
    parser.add_argument("--create-pr", action="store_true", help="Automatically create a PR if optimizations are found")
    parser.add_argument("--repo-url", help="GitHub Repository URL (required for Auto-PR)")
    parser.add_argument("--github-token", help="GitHub Personal Access Token (required for Auto-PR)")
    
    args = parser.parse_args()
    scan_dockerfile(args.api_url, args.file, args.create_pr, args.repo_url, args.github_token)
