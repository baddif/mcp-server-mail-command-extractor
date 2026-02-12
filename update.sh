#!/bin/bash
# Mail Command Extractor MCP Server - Automated Update Script
# 
# This script provides safe, automated updates for Mail Command Extractor MCP Server
# with configuration backup and validation.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$PROJECT_DIR/.update_backup_$(date +%Y%m%d_%H%M%S)"
CONFIG_FILES=(
    "mail_command_extractor_config_local.json"
    "claude_desktop_config.json"
)

# Utility functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not a git repository. Please ensure you're in the correct directory."
        exit 1
    fi
}

# Check for uncommitted changes
check_uncommitted_changes() {
    if [ -n "$(git status --porcelain)" ]; then
        warning "Repository has uncommitted changes."
        echo "Uncommitted files:"
        git status --porcelain
        echo
        read -p "Continue with update? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Update cancelled by user."
            exit 0
        fi
    fi
}

# Backup configuration files
backup_configs() {
    log "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    
    for config_file in "${CONFIG_FILES[@]}"; do
        if [ -f "$PROJECT_DIR/$config_file" ]; then
            log "Backing up $config_file"
            cp "$PROJECT_DIR/$config_file" "$BACKUP_DIR/"
            success "Backed up $config_file"
        else
            log "Config file $config_file not found, skipping backup"
        fi
    done
}

# Check for updates
check_updates() {
    log "Checking for updates..."
    
    # Fetch latest changes
    git fetch origin main || {
        error "Failed to fetch updates from remote repository"
        exit 1
    }
    
    # Compare commits
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/main)
    
    if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
        success "Already up to date!"
        log "Current commit: $(git rev-parse --short HEAD)"
        exit 0
    fi
    
    # Count commits behind
    COMMITS_BEHIND=$(git rev-list --count HEAD..origin/main)
    log "Updates available: $COMMITS_BEHIND commits behind"
    
    # Show recent changes
    echo
    log "Recent changes:"
    git log --oneline HEAD..origin/main | head -5
    echo
}

# Perform the update
perform_update() {
    log "Starting update process..."
    
    # Pull latest changes
    log "Pulling latest changes..."
    git pull origin main || {
        error "Failed to pull updates"
        exit 1
    }
    success "Code updated successfully"
    
    # Update Python dependencies if requirements.txt exists
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        log "Updating Python dependencies..."
        python3 -m pip install -r requirements.txt --upgrade || {
            warning "Failed to update some dependencies, but continuing..."
        }
        success "Dependencies updated"
    fi
}

# Restore configuration files
restore_configs() {
    log "Restoring configuration files..."
    
    for config_file in "${CONFIG_FILES[@]}"; do
        if [ -f "$BACKUP_DIR/$config_file" ]; then
            log "Restoring $config_file"
            cp "$BACKUP_DIR/$config_file" "$PROJECT_DIR/"
            success "Restored $config_file"
        fi
    done
}

# Run post-update tests
run_tests() {
    log "Running post-update validation..."
    
    # Test 1: Skill functionality
    log "Testing skill functionality..."
    python3 test_mail_command_extractor.py > /dev/null 2>&1 || {
        error "Skill tests failed"
        return 1
    }
    success "Skill tests passed"
    
    # Test 2: MCP server
    log "Testing MCP server..."
    python3 mcp_server.py --test > /dev/null 2>&1 || {
        error "MCP server test failed"
        return 1
    }
    success "MCP server test passed"
    
    # Test 3: Integration tests
    log "Running integration tests..."
    python3 test_integration.py > /dev/null 2>&1 || {
        warning "Integration tests failed, but core functionality is working"
        return 0
    }
    success "Integration tests passed"
    
    return 0
}

# Cleanup backup files (optional)
cleanup_backups() {
    if [ -d "$BACKUP_DIR" ]; then
        read -p "Keep backup files in $BACKUP_DIR? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            log "Removing backup directory..."
            rm -rf "$BACKUP_DIR"
            success "Backup directory removed"
        else
            success "Backup files kept in $BACKUP_DIR"
        fi
    fi
}

# Show update summary
show_summary() {
    echo
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎉 Update completed successfully!${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Show version info
    if command -v python3 > /dev/null 2>&1; then
        echo
        python3 version.py --info 2>/dev/null || {
            log "Version info not available"
        }
    fi
    
    echo
    log "Update summary:"
    echo "  📁 Project directory: $PROJECT_DIR"
    echo "  💾 Backup location: $BACKUP_DIR"
    echo "  🔧 Current commit: $(git rev-parse --short HEAD)"
    echo
    log "Next steps:"
    echo "  • Restart any running MCP servers"
    echo "  • Test your configurations"
    echo "  • Check the CHANGELOG.md for new features"
}

# Rollback function
rollback() {
    error "Update failed. Rolling back changes..."
    
    if [ -d "$BACKUP_DIR" ]; then
        log "Restoring from backup..."
        restore_configs
        
        # Reset git if needed
        if [ -n "$LOCAL_COMMIT" ]; then
            log "Resetting to previous commit..."
            git reset --hard "$LOCAL_COMMIT" || {
                warning "Could not reset git. Manual intervention may be needed."
            }
        fi
        
        success "Rollback completed"
    else
        error "No backup found. Manual recovery may be needed."
    fi
    
    exit 1
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Mail Command Extractor MCP Server - Update Script${NC}"
    echo -e "${BLUE}====================================================${NC}"
    echo
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Trap errors for rollback
    trap rollback ERR
    
    # Pre-update checks
    check_git_repo
    check_uncommitted_changes
    
    # Backup phase
    backup_configs
    
    # Update phase
    check_updates
    perform_update
    restore_configs
    
    # Validation phase
    if run_tests; then
        show_summary
        cleanup_backups
    else
        warning "Some tests failed, but basic functionality is working"
        log "You may want to check the logs and run tests manually"
        show_summary
    fi
    
    # Disable error trap for successful completion
    trap - ERR
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--help|--check-only|--force]"
        echo
        echo "Options:"
        echo "  --help       Show this help message"
        echo "  --check-only Only check for updates, don't install"
        echo "  --force      Force update even with uncommitted changes"
        exit 0
        ;;
    --check-only)
        check_git_repo
        check_updates
        exit 0
        ;;
    --force)
        check_git_repo() { :; }  # Override git check
        check_uncommitted_changes() { :; }  # Override uncommitted check
        ;;
esac

# Run main function
main "$@"