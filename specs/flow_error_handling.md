# Flow: Error Handling in ClaudeCodeChatModel

## Description
Validates that the Claude Code adapter gracefully handles various error conditions and provides meaningful feedback to users when issues occur.

## User Journey

### CLI Not Installed Flow
1. User attempts to create ClaudeCodeChatModel instance
2. System detects Claude Code CLI is not available
3. User receives clear error message with installation instructions
4. User installs CLI following the provided instructions
5. User successfully creates model instance after CLI installation

### Invalid Model Configuration Flow
1. User creates model with invalid parameters (e.g., temperature > 1.0)
2. User attempts to invoke the model
3. System validates parameters and returns descriptive error
4. User corrects the parameters
5. User successfully uses the model with valid configuration

### Network/Process Error Flow
1. User successfully creates model instance
2. User invokes model but Claude Code process fails
3. System catches the process error
4. User receives RuntimeError with exit code and stderr details
5. User can retry or handle the error appropriately

### Response Parsing Error Flow
1. User invokes model successfully
2. Claude Code returns malformed JSON response
3. System detects JSON decode error
4. User receives error with the problematic line identified
5. User can report issue or retry with different input

### Timeout Handling Flow
1. User sends a complex request requiring long processing
2. Request exceeds reasonable time limit
3. System handles timeout gracefully
4. User receives timeout error message
5. User can adjust timeout settings or simplify request

### Session Disconnection Flow
1. User creates model with continuous session enabled
2. User actively uses the session
3. Session unexpectedly disconnects (network issue, CLI crash)
4. System detects disconnection
5. User receives error and can reconnect or create new session

## Expected Error Messages

Each error should provide:
- Clear description of what went wrong
- Specific error type (CLINotFoundError, ProcessError, etc.)
- Actionable recovery steps
- Relevant context (exit codes, stderr output)

## Success Criteria
- All errors are caught and wrapped appropriately
- No silent failures or undefined behavior
- Error messages guide users to resolution
- System remains stable after errors
- Errors don't leak implementation details unnecessarily