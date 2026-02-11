import sys
import os
import requests
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Dockerfile Optimizer Gate CLI")
    parser.add_argument("--file", default="Dockerfile", help="Path to the Dockerfile")
    parser.add_argument("--server", required=True, help="Base URL of the Optimizer API")
    parser.add_argument("--apply", action="store_true", help="Apply optimizations locally")
    parser.add_argument("--create-pr", action="store_true", help="Consent via Pull Request")
    parser.add_argument("--fail-on", choices=["CRITICAL", "HIGH", "ALL"], help="Fail build on security risks")
    parser.add_argument("--repo-url", help="GitHub Repo URL (for PR)")
    parser.add_argument("--github-token", help="GitHub Token (for PR)")
    
    args = parser.parse_args()

    server_url = args.server.rstrip('/')
    api_url = server_url if server_url.endswith('/api') else f"{server_url}/api"

    if not os.path.exists(args.file):
        print(f"❌ Error: {args.file} not found.")
        sys.exit(1)

    print(f"🔍 Reading {args.file}...")
    with open(args.file, 'r') as f:
        content = f.read()

    print(f"📡 Sending to Optimizer Service ({api_url})...")
    
    try:
        response = requests.post(f"{api_url}/analyze-dockerfile", json={"content": content}, timeout=60)
        response.raise_for_status()
        report = response.json()

        recommendation = report.get("recommendation", {})
        security_warnings = recommendation.get("security_warnings", [])
        optimized_content = recommendation.get("optimized_dockerfile")

        print("\n--- 🔎 Analysis Findings ---")
        if security_warnings:
            for w in security_warnings:
                print(f"  ⚠️ {w}")
        else:
            print("  ✅ No critical security issues found.")

        # LOGIC FOR CHOICE/CONSENT
        if optimized_content:
            if args.apply:
                print(f"\n✨ Swapping {args.file} with optimized version...")
                with open(args.file, 'w') as f:
                    f.write(optimized_content)
                print("✅ Done! Build will now use the optimized file.")

            elif args.create_pr:
                def normalize(c):
                    return "\n".join(l.strip() for l in c.replace("\r\n", "\n").strip().splitlines() if l.strip())
                
                if normalize(optimized_content) == normalize(content):
                    print("\n✅ Your Dockerfile is already fully optimized! No PR needed.")
                    print("🎉 Analysis Complete. Proceeding with build.")
                    sys.exit(0)

                if not args.repo_url:
                    print("❌ Error: --repo-url is required for --create-pr")
                    sys.exit(1)
                
                print(f"\n🚀 Registering Optimization Request for {args.repo_url}...")
                
                consent_payload = {
                    "url": args.repo_url,
                    "path": args.file,
                    "original_content": content,
                    "optimized_content": optimized_content
                }
                
                try:
                    consent_resp = requests.post(f"{api_url}/consent/register", json=consent_payload)
                    consent_resp.raise_for_status()
                    consent_id = consent_resp.json().get("consent_id")
                    
                    # For demo purposes, we derive the frontend URL from the server URL or use a default
                    frontend_base = server_url.replace("app-optimizer", "optimizer-ui").replace(":8000", ":5173")
                    # If on local dev uvicorn
                    if "localhost:8000" in frontend_base:
                        frontend_base = "http://localhost:5173"
                    elif "azurewebsites.net" in frontend_base:
                         # Assume frontend is at the root of the same app or a sibling app
                         frontend_base = server_url.replace("/api", "") 

                    review_url = f"{frontend_base}/review/{consent_id}"
                    
                    print(f"\n✨ Optimization Ready for Review!")
                    print(f"👉 Please approve the changes here:")
                    print(f"🔗 {review_url}")
                    print(f"\n💡 Our Bot will create the PR ONLY after you click 'Approve'.")
                except Exception as e:
                    print(f"❌ Failed to register optimization: {e}")
            else:
                print("\n💡 NOTE: Use --apply to swap files locally or --create-pr to request permission via PR.")
        else:
            print("\nℹ️ No optimizations recommended at this time.")

        # Policy Gate
        if args.fail_on:
            fail = False
            if args.fail_on == "ALL" and security_warnings: fail = True
            elif args.fail_on == "CRITICAL" and any("[CRITICAL]" in w or "[RUN_AS_ROOT]" in w for w in security_warnings): fail = True
            elif args.fail_on == "HIGH" and any("[CRITICAL]" in w or "[HIGH]" in w or "[RUN_AS_ROOT]" in w for w in security_warnings): fail = True
            
            if fail:
                print("\n🛑 ABORTING: Security policy violation detected.")
                sys.exit(1)

        print("\n🎉 Analysis Complete. Proceeding with build.")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
