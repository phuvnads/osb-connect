# OSB Connect

AI marketing automation for Vietnamese small businesses, freelancers and solo marketers.

OSB Connect reads a small "brain" folder of Markdown notes about you (who you are, how you write, which words you always fix), asks Claude to write posts in your voice, keeps them in a simple queue you can open in Excel, and publishes the approved ones through official platform APIs.

> Status: early version (0.1). Core flow works: write → review → approve → publish to a Facebook Page. More platforms are on the roadmap.

[Tiếng Việt bên dưới](#tiếng-việt)

## Why

Most marketing automation tools are built for English-speaking markets, priced in USD, and assume technical skills. AI writing tools write generic text because they know nothing about you. OSB Connect keeps your context in plain Markdown files (works great with an Obsidian vault), so every post starts from your real profile and voice.

## Principles

- **Your data stays on your machine.** The brain is a folder of text files you own.
- **Nothing is posted without a human OK.** New posts are drafts. Only rows marked `approved` are published.
- **Dry run by default.** `run` only prints what it would send until you add `--live`.
- **Official APIs only.** No browser automation, no fake accounts.
- **No invented facts.** The writer is told never to make up stories, numbers or customers, and to leave `[ĐIỀN: ...]` placeholders instead.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env          # add your ANTHROPIC_API_KEY, FB_PAGE_ID, FB_PAGE_TOKEN

# 1. Write a post from your brain folder and add it to the queue as a draft
python -m osb_connect write --brain examples/brain \
  --topic "Vì sao AI trả lời chung chung, và cách cho AI hiểu việc của bạn" \
  --add-to queue.csv --at "2026-11-05 08:00"

# 2. Review the queue (open queue.csv in Excel or Google Sheets to edit text)
python -m osb_connect list --queue queue.csv

# 3. Approve a draft
python -m osb_connect approve --queue queue.csv --id 1

# 4. Publish approved posts that are due (dry run first, then --live)
python -m osb_connect run --queue queue.csv
python -m osb_connect run --queue queue.csv --live
```

Schedule step 4 with Windows Task Scheduler or cron to post automatically.

## The brain folder

| File | What to put in it |
|---|---|
| `profile.md` | Who you are, what you sell, who your customers are, their pain points |
| `voice.md` | How you write: pronouns, sentence length, things you never do |
| `word-fixes.md` | A two-column table. Every time you fix a word the AI wrote, add a row. Fixes are applied automatically |

See `examples/brain/` for a full example.

## Project layout

```
osb_connect/
  brain.py       load profile, voice and word fixes from Markdown
  writer.py      write a post with Claude (claude-opus-5-5)
  queue.py       CSV post queue: draft → approved → posted / failed
  publishers.py  official API publishers (Facebook Page now)
  cli.py         command line interface
examples/        sample brain folder and queue
tests/           unit tests (no network needed)
```

## Roadmap

- [ ] Scheduled posts via the Facebook Graph API `scheduled_publish_time`
- [ ] Publishers: Instagram (Graph API), YouTube community/description updates, Zalo OA
- [ ] Generate several variants per topic for A/B testing
- [ ] Learn new word fixes automatically from your edits in the queue
- [ ] Simple local web UI for non-technical users

## Development

```bash
python -m unittest discover -s tests
```

Contributions are welcome. Please open an issue first for larger changes.

## License

MIT, see [LICENSE](LICENSE).

---

## Tiếng Việt

OSB Connect giúp chủ shop nhỏ, người làm marketing online tự động hoá việc viết và đăng bài.

- Bạn ghi thông tin về mình vào vài file chữ: mình là ai, viết giọng thế nào, chữ nào hay phải sửa.
- OSB Connect nhờ Claude viết bài đúng giọng của bạn, lưu vào danh sách bài chờ (mở được bằng Excel).
- Bạn duyệt bài nào thì bài đó mới được đăng, qua API chính thức của nền tảng.

Nguyên tắc: dữ liệu nằm trên máy của bạn, không đăng gì khi chưa duyệt, mặc định chạy thử, chỉ dùng API chính thức, không bịa số liệu.

Bắt đầu nhanh: xem mục Quick start ở trên. Thư mục mẫu: `examples/brain/`.

## Author

Built and maintained by Nguyen Van Phu ([@phuvnads](https://github.com/phuvnads)), more than 10 years in online marketing.
