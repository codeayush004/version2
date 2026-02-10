import sys
import os
import requests
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Antigravity Optimization Gate CLI")
    parser.add_argument("--file", default="Dockerfile", help="Path to the Dockerfile")
    parser.add_argument("--server", required=True, help="Base URL of the Optimizer API (e.g. http://localhost:8000)")
    parser.add_argument("--apply", action="store_true", help="Apply the optimized Dockerfile by overwriting the local file")
    parser.add_argument("--fail-on", choices=["CRITICAL", "HIGH", "ALL"], help="Fail the build if specific severity levels are found")
    
    args = parser.parse_args()

    # Normalize server URL
    server_url = args.server.rstrip('/')
    if server_url.endswith('/api'):
        api_url = server_url
    else:
        api_url = f"{server_url}/api"

    if not os.path.exists(args.file):
        print(f"❌ Error: {args.file} not found.")
        sys.exit(1)

    with open(args.file, 'r') as f:
        content = f.read()

    print(f"🔍 Analyzing {args.file}...")
    
    try:
        response = requests.post(
            f"{api_url}/analyze-dockerfile",
            json={"content": content},
            timeout=60
        )
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
            print("  ✅ No critical security warnings found.")

        # Apply logic
        if args.apply and optimized_content:
            print(f"\n✨ Applying optimizations to {args.file}...")
            with open(args.file, 'w') as f:
                f.write(optimized_content)
            print("✅ File updated successfully.")
        
        # Failure logic
        if args.fail_on:
            fail = False
            if args.fail_on == "ALL" and security_warnings:
                fail = True
            elif args.fail_on == "CRITICAL" and any("[CRITICAL]" in w or "[RUN_AS_ROOT]" in w for w in security_warnings):
                fail = True
            elif args.fail_on == "HIGH" and any("[CRITICAL]" in w or "[HIGH]" in w or "[RUN_AS_ROOT]" in w for w in security_warnings):
                fail = True
            
            if fail:
                print("\n🛑 CI Status: FAILED due to security policies.")
                sys.exit(1)

        print("\n🎉 CI Status: PASSED")
        sys.exit(0)

    except Exception as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
