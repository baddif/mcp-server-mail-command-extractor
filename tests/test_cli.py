import json
from subprocess import run, PIPE
from pathlib import Path

def test_cli_with_file(tmp_path):
    # prepare emails file
    emails = [
        {"sender": "A <a@example.com>", "sender_email": "a@example.com", "subject": "日报", "content": "生成日报", "date_received": "2026-02-12T10:00:00Z", "email_id": "e1"}
    ]
    rules = {"rules": [{"sender": "a@example.com", "subjects": ["日报"], "contents": [], "action": "generate_daily_report"}]}

    emails_file = tmp_path / 'emails.json'
    rules_file = tmp_path / 'rules.json'
    emails_file.write_text(json.dumps(emails, ensure_ascii=False))
    rules_file.write_text(json.dumps(rules, ensure_ascii=False))

    # run CLI
    proc = run(['python3', 'main.py', str(emails_file), str(rules_file)], stdout=PIPE, stderr=PIPE, text=True)
    assert proc.returncode == 0
    out = proc.stdout.strip()
    assert out
    result = json.loads(out)
    assert result['success'] is True
    assert 'extracted_commands' in result['data']
