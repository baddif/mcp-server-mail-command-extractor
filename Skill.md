# Mail Command Extractor Skill

This skill extracts actionable commands from a list of emails using detection rules.

## Input Schema

- `emails` (required): array of email objects (directly the `matched_emails` array from gmail_check output)
  - each email object fields (required): `sender`, `sender_email`, `subject`, `content`, `date_received`, `email_id`

- `detection_rules` (required): object containing `rules` array. Each rule:
  - `sender` (required): exact email address to match against `sender_email` (case-insensitive)
  - `subjects` (optional): array of title keywords (string). Title matches if any keyword is contained in subject.
  - `contents` (optional): array of content keywords (string). Content matches if any keyword is contained in content.
  - `action` (required): command name to produce
  - `parameters` (optional): object, passed through to the produced command
  - `priority` (optional): integer priority (lower is higher priority)

- `merge_duplicates` (optional): boolean, default true

## Output Schema

All outputs MUST follow the core contract:

Success:

```json
{
  "success": true,
  "data": {
    "extracted_commands": [
      {
        "command": "...",
        "parameters": {...},
        "priority": 10,
        "matched_emails": [ ... ],
        "matching_details": { ... }
      }
    ],
    "processed_emails": 10,
    "matched_emails": 3,
    "total_commands": 3,
    "processing_time": "..."
  },
  "error": null
}
```

Error:

```json
{
  "success": false,
  "data": null,
  "error": "Error message"
}
```

## Example CLI

```bash
# Using files
python main.py emails.json rules.json

# Using JSON strings
python main.py '[{"sender": "a <a@example.com>", "sender_email": "a@example.com", "subject": "日报", "content": "生成日报", "date_received": "...", "email_id": "1"}]' '{"rules": [{"sender": "a@example.com", "subjects":["日报"], "action": "generate_daily_report"}]}'
```

## Example MCP request/response

Request (tool call):

```json
{ "method": "tools/call", "params": { "name": "mail_command_extractor", "arguments": { "emails": [ ... ], "detection_rules": { ... } } } }
```

Response (tool returns content block with JSON string):

```json
{ "content": [{ "type": "text", "text": "{\"success\": true, \"data\": {...}, \"error\": null }" }] }
```

## Testing

- Tests MUST include CLI and MCP invocation tests. See `tests/`.
