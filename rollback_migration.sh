#!/bin/bash
# 🚨 EMERGENCY ROLLBACK SCRIPT
# Instantly restore system to pre-migration state

echo "🚨 EMERGENCY ROLLBACK: Restoring to pre-migration state..."

# Check if backup branch exists
if git show-ref --verify --quiet refs/heads/backup/pre-opportunity-migration; then
    echo "✅ Backup branch found: backup/pre-opportunity-migration"
    
    # Switch to backup branch
    git checkout backup/pre-opportunity-migration
    echo "✅ Switched to backup branch"
    
    # Delete migration branch if it exists
    if git show-ref --verify --quiet refs/heads/feature/opportunity-migration; then
        git branch -D feature/opportunity-migration
        echo "✅ Deleted migration branch"
    fi
    
    # Switch back to main and reset to backup state
    git checkout main
    git reset --hard backup/pre-opportunity-migration
    echo "✅ Main branch restored to pre-migration state"
    
    echo ""
    echo "🎯 ROLLBACK COMPLETE!"
    echo "   System restored to pre-migration state"
    echo "   All migration changes have been removed"
    echo "   Original clinical-focused system is active"
    echo ""
    echo "To verify system is working:"
    echo "   streamlit run streamlit_app.py"
    echo ""
    
else
    echo "❌ ERROR: Backup branch not found!"
    echo "   Cannot perform rollback without backup"
    echo "   Manual recovery may be required"
    exit 1
fi 