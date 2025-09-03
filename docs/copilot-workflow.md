# 🤖 Copilot Auto-PR Workflow

## Overview

This workflow automatically creates draft Pull Requests for GitHub issues that have sufficient context for AI-assisted development using GitHub Copilot.

## How It Works

### Triggers

The workflow triggers on:
1. **Issue events**: opened, edited, labeled
2. **Workflow completion**: After the "Bug Reproduction Info Check" workflow completes successfully

### Process Flow

1. **Issue Analysis**: Uses AI to analyze the issue content and determine if it has sufficient context for development work
2. **Context Check**: Verifies the issue includes:
   - Clear problem description or feature specification
   - Technical details about expected behavior
   - Context about relevant code files or functions
   - For bugs: reproduction steps, expected vs actual behavior
   - For features: clear implementation requirements

3. **PR Creation**: If the issue has sufficient context:
   - Creates a new feature branch with naming pattern: `copilot/issue-{number}-{title-slug}`
   - Creates a draft PR linking to the original issue
   - Adds a comment to the issue with the PR link

4. **Feedback**: If context is insufficient, comments on the issue with specific guidance on what information is needed

### Integration with GitHub Copilot

Once a draft PR is created, developers can:
- Open the PR in GitHub Copilot Workspace
- Use Copilot suggestions to implement changes
- Leverage AI assistance for code generation and problem-solving
- Review and refine the implementation before marking PR as ready for review

## Workflow Configuration

### Required Permissions

```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
  actions: read
```

### AI Models Used

- **Context Analysis**: `openai/gpt-4o-mini` - Analyzes issue content for development readiness
- **Integration**: Works with existing `bug-reproduction-check.yml` workflow

### Branch Naming Convention

Branches are automatically created with the pattern:
- `copilot/issue-{issue_number}-{sanitized-title}`
- Titles are converted to lowercase, non-alphanumeric characters become dashes
- Limited to 60 characters for GitHub compatibility

## Example Workflow

1. **User creates issue**: "Bug: Log parser crashes on malformed timestamps"
2. **AI Analysis**: Determines issue has sufficient context (reproduction steps, expected behavior)
3. **Branch Creation**: `copilot/issue-123-bug-log-parser-crashes-on-malformed-timestamps`
4. **Draft PR**: Created with template and linked to original issue
5. **Copilot Development**: Developer uses Copilot Workspace to implement fix
6. **Review Process**: PR marked ready when implementation complete

## Benefits

- **Faster Development**: Automatically creates development environment when issues are ready
- **Better Issue Quality**: Provides feedback to improve issue descriptions
- **Streamlined Workflow**: Reduces manual PR creation and branch management
- **AI-Powered Development**: Enables immediate Copilot assistance for qualified issues
- **Duplicate Prevention**: Checks for existing PRs before creating new ones

## Configuration

The workflow can be customized by modifying:
- AI prompts for context analysis
- Branch naming patterns
- PR template content
- Trigger conditions

## Troubleshooting

- **No PR created**: Check if issue has sufficient context based on AI analysis feedback
- **Duplicate PRs**: Workflow automatically prevents duplicates by checking existing PRs
- **Branch conflicts**: Uses timestamp-based branch names to avoid conflicts