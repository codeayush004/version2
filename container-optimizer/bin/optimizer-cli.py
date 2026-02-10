import sys
import os
import requests
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Antigravity Optimization Gate CLI")
    parser.add_argument("--file", default="Dockerfile", help="Path to the Dockerfile")
    parser.add_argument("--server", required=True, help="Base URL of the Optimizer API (e.g. http://localhost:8000)")
    parser.add_argument("--apply", action="store_true", help="Apply optimizations locally by overwriting the file")
    parser.add_argument("--create-pr", action="store_true", help="Request consent via a GitHub Pull Request")
    parser.add_argument("--fail-on", choices=["CRITICAL", "HIGH", "ALL"], help="Fail build if security risks are found")
    
    # Credentials for PR
    parser.add_argument("--repo-url", help="GitHub Repo URL (required for PR)")
    parser.add_argument("--github-token", help="GitHub Token (required for PR)")
    
    args = parser.parse_args()

    # Normalize server URL
    server_url = args.server.rstrip('/')
    api_url = server_url if server_url.endswith('/api') else f"{server_url}/api"

    if not os.path.exists(args.file):
        print(f"❌ Error: {args.file} not found.")
        sys.exit(1)

    with open(args.file, 'r') as f:
        content = f.read()

    print(f"🔍 Analyzing {args.file}...")
    
    try:
        response = requests.post(f"{api_url}/analyze-dockerfile", json={"content": content}, timeout=60)
        response.raise_for_status()
        report = response.json()

        recommendation = report.get("recommendation", {})
        security_warnings = recommendation.get("security_warnings", [])
        optimized_content = recommendation.get("optimized_dockerfile")

        print("\n--- Findings ---")
        if security_warnings:
            for w in security_warnings:
                print(f"  ⚠️ {w}")
        else:
            print("  ✅ No security issues detected.")

        # CONSENT FLOW A: Local Apply (Immediate)
        if args.apply and optimized_content:
            print(f"\n✨ Overwriting {args.file} with optimized version...")
            with open(args.file, 'w') as f:
                f.write(optimized_content)
            print("✅ File updated.")

        # CONSENT FLOW B: Pull Request (Review & Merge)
        if args.create_pr and optimized_content:
            if not args.repo_url or not args.github_token:
                print("❌ Error: --repo-url and --github-token required for --create-pr")
                sys.exit(1)
            
            print("\n🚀 Requesting consent via Pull Request...")
            pr_payload = {
                "url": args.repo_url,
                "updates": [{"path": args.file, "content": optimized_content}],
                "token": args.github_token,
                "pr_title": "✨ [Optimizer] Dockerfile Hardening & Optimization",
                "commit_message": "Chore: Applied container security optimizations"
            }
            pr_resp = requests.post(f"{api_url}/create-bulk-pr", json=pr_payload)
            if pr_resp.status_code == 200:
                print(f"✅ Success! View PR: {pr_resp.json().get('message')}")
            else:
                print(f"❌ PR Creation Failed: {pr_resp.text}")
        
        # Policy Enforcement
        if args.fail_on:
            fail = False
            if args.fail_on == "ALL" and security_warnings:
                fail = True
            elif args.fail_on == "CRITICAL" and any("[CRITICAL]" in w or "[RUN_AS_ROOT]" in w for w in security_warnings):
                fail = True
            elif args.fail_on == "HIGH" and any("[CRITICAL]" in w or "[HIGH]" in w or "[RUN_AS_ROOT]" in w for w in security_warnings):
                fail = True
            
            if fail:
                print("\n🛑 CI Status: FAILED (Policy violation)")
                sys.exit(1)

        print("\n🎉 CI Status: PASSED")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
