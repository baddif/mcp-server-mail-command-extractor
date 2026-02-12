#!/usr/bin/env python3
"""
Version Management for Mail Command Extractor MCP Server

This module provides version information and update utilities for the
Mail Command Extractor MCP Server project.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

# Current version information
__version__ = "1.0.0"
__release_date__ = "2026-02-12"
__compatibility_version__ = "2024-11-05"  # MCP protocol version

# Version metadata
VERSION_INFO = {
    "version": __version__,
    "release_date": __release_date__,
    "mcp_compatibility": __compatibility_version__,
    "python_min_version": "3.7",
    "features": [
        "Intelligent Email Detection",
        "Command Generation",
        "Fuzzy Pattern Matching", 
        "Priority-based Sorting",
        "Duplicate Command Merging",
        "MCP Protocol Support",
        "Multi-rule Processing",
        "Context-aware Processing"
    ]
}

def get_version_info() -> Dict[str, Any]:
    """
    Get comprehensive version information
    
    Returns:
        dict: Version information including current version, features, and compatibility
    """
    return VERSION_INFO.copy()

def get_version_string() -> str:
    """
    Get formatted version string
    
    Returns:
        str: Formatted version string
    """
    return f"Mail Command Extractor MCP Server v{__version__} (MCP {__compatibility_version__})"

def check_git_status() -> Optional[Dict[str, Any]]:
    """
    Check Git repository status for version tracking
    
    Returns:
        dict: Git status information or None if not a git repo
    """
    try:
        # Get current commit hash
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Get current branch
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Check if there are uncommitted changes
        status_output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        has_changes = bool(status_output)
        
        # Get latest tag
        try:
            latest_tag = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except subprocess.CalledProcessError:
            latest_tag = None
            
        return {
            "commit_hash": commit_hash[:8],  # Short hash
            "full_commit_hash": commit_hash,
            "branch": branch,
            "has_uncommitted_changes": has_changes,
            "latest_tag": latest_tag,
            "is_clean": not has_changes
        }
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def check_for_updates() -> Dict[str, Any]:
    """
    Check if updates are available from remote repository
    
    Returns:
        dict: Update status information
    """
    update_info = {
        "update_available": False,
        "current_version": __version__,
        "remote_version": None,
        "update_instructions": [],
        "git_status": check_git_status()
    }
    
    try:
        # Fetch latest changes from remote
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            check=True
        )
        
        # Compare local and remote commits
        local_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        ).decode().strip()
        
        remote_commit = subprocess.check_output(
            ["git", "rev-parse", "origin/main"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        ).decode().strip()
        
        if local_commit != remote_commit:
            update_info["update_available"] = True
            update_info["update_instructions"] = [
                "Updates available! Run the update command:",
                "python3 version.py --update",
                "Or manually: git pull origin main && pip install -r requirements.txt"
            ]
            
        # Get commit count difference
        try:
            commits_behind = subprocess.check_output(
                ["git", "rev-list", "--count", f"{local_commit}..{remote_commit}"],
                cwd=os.path.dirname(os.path.abspath(__file__))
            ).decode().strip()
            
            if int(commits_behind) > 0:
                update_info["commits_behind"] = int(commits_behind)
        except subprocess.CalledProcessError:
            pass
            
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        update_info["check_error"] = str(e)
        update_info["update_instructions"] = [
            "Could not check for updates automatically.",
            "Please check the repository manually:",
            "https://github.com/baddif/mcp-server-mail-command-extractor"
        ]
    
    return update_info

def perform_update() -> Dict[str, Any]:
    """
    Perform automatic update from Git repository
    
    Returns:
        dict: Update result information
    """
    result = {
        "success": False,
        "message": "",
        "previous_version": __version__,
        "steps_completed": []
    }
    
    try:
        # Check current Git status
        git_status = check_git_status()
        if not git_status:
            result["message"] = "Not a Git repository. Please update manually."
            return result
            
        if git_status["has_uncommitted_changes"]:
            result["message"] = "Repository has uncommitted changes. Please commit or stash changes before updating."
            return result
        
        # Step 1: Fetch latest changes
        print("📡 Fetching latest changes...")
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True,
            capture_output=True
        )
        result["steps_completed"].append("Fetched remote changes")
        
        # Step 2: Pull changes
        print("⬇️  Pulling updates...")
        pull_result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True,
            capture_output=True,
            text=True
        )
        result["steps_completed"].append("Pulled code updates")
        
        # Step 3: Update Python dependencies
        print("📦 Updating dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True,
            capture_output=True
        )
        result["steps_completed"].append("Updated Python dependencies")
        
        # Step 4: Run post-update validation
        print("✅ Validating update...")
        subprocess.run(
            [sys.executable, "test_mail_command_extractor.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True,
            capture_output=True
        )
        result["steps_completed"].append("Validated skill functionality")
        
        # Step 5: Test MCP server
        subprocess.run(
            [sys.executable, "mcp_server.py", "--test"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True,
            capture_output=True
        )
        result["steps_completed"].append("Validated MCP server functionality")
        
        result["success"] = True
        result["message"] = "Update completed successfully!"
        
        # Get new version info
        new_git_status = check_git_status()
        if new_git_status:
            result["new_commit"] = new_git_status["commit_hash"]
            
    except subprocess.CalledProcessError as e:
        result["message"] = f"Update failed: {e}"
        result["error_details"] = e.stderr.decode() if e.stderr else str(e)
    except Exception as e:
        result["message"] = f"Unexpected error during update: {e}"
        
    return result

def show_version_info():
    """Display comprehensive version information"""
    info = get_version_info()
    git_info = check_git_status()
    
    print(f"🚀 {get_version_string()}")
    print("=" * 70)
    print(f"📅 Release Date: {info['release_date']}")
    print(f"🐍 Python Requirement: {info['python_min_version']}+")
    print(f"🔧 MCP Protocol: {info['mcp_compatibility']}")
    
    if git_info:
        print(f"📍 Git Branch: {git_info['branch']}")
        print(f"🔗 Commit: {git_info['commit_hash']}")
        if git_info['latest_tag']:
            print(f"🏷️  Latest Tag: {git_info['latest_tag']}")
        if git_info['has_uncommitted_changes']:
            print("⚠️  Repository has uncommitted changes")
        else:
            print("✅ Repository is clean")
    
    print(f"\n✨ Features:")
    for feature in info['features']:
        print(f"   • {feature}")

def main():
    """Command-line interface for version management"""
    if len(sys.argv) < 2:
        show_version_info()
        return
    
    command = sys.argv[1]
    
    if command == "--version" or command == "-v":
        print(get_version_string())
        
    elif command == "--info":
        show_version_info()
        
    elif command == "--check-updates":
        print("🔍 Checking for updates...")
        update_info = check_for_updates()
        
        if update_info["update_available"]:
            print("🆕 Updates available!")
            if "commits_behind" in update_info:
                print(f"📊 {update_info['commits_behind']} commits behind")
            print("\nTo update:")
            for instruction in update_info["update_instructions"]:
                print(f"   {instruction}")
        else:
            print("✅ You are up to date!")
            
        if "check_error" in update_info:
            print(f"⚠️  {update_info['check_error']}")
            
    elif command == "--update":
        print("🔄 Starting update process...")
        result = perform_update()
        
        print(f"\n📋 Steps completed:")
        for step in result["steps_completed"]:
            print(f"   ✅ {step}")
            
        if result["success"]:
            print(f"\n🎉 {result['message']}")
            if "new_commit" in result:
                print(f"📍 Now on commit: {result['new_commit']}")
        else:
            print(f"\n❌ {result['message']}")
            if "error_details" in result:
                print(f"Error details: {result['error_details']}")
                
    elif command == "--json":
        # Output version info as JSON for programmatic use
        version_data = {
            "version_info": get_version_info(),
            "git_status": check_git_status(),
            "update_check": check_for_updates()
        }
        print(json.dumps(version_data, indent=2, ensure_ascii=False))
        
    else:
        print("Usage: python3 version.py [--version|--info|--check-updates|--update|--json]")
        print("\nOptions:")
        print("  --version, -v     Show version string")
        print("  --info           Show detailed version information")
        print("  --check-updates  Check if updates are available")
        print("  --update         Perform automatic update")
        print("  --json           Output version data as JSON")

if __name__ == "__main__":
    main()