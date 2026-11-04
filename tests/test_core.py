import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from osb_connect import publishers, queue
from osb_connect.brain import Brain, parse_word_fixes
from osb_connect.writer import build_request

EXAMPLE_BRAIN = Path(__file__).resolve().parent.parent / "examples" / "brain"


class BrainTest(unittest.TestCase):
    def test_load_example(self):
        brain = Brain.load(EXAMPLE_BRAIN)
        self.assertIn("Nguyễn Văn Phú", brain.profile)
        self.assertIn(("hòm thư", "hộp thư"), brain.word_fixes)

    def test_parse_skips_header_and_separator(self):
        md = "| Tránh viết | Viết thế này |\n|---|---|\n| a | b |\n"
        self.assertEqual(parse_word_fixes(md), [("a", "b")])

    def test_apply_word_fixes_and_dash(self):
        brain = Brain(word_fixes=[("hòm thư", "hộp thư")])
        self.assertEqual(brain.apply_word_fixes("Mở hòm thư — xem ngay"), "Mở hộp thư, xem ngay")

    def test_system_prompt_contains_context(self):
        prompt = Brain.load(EXAMPLE_BRAIN).system_prompt()
        self.assertIn("## Profile", prompt)
        self.assertIn("## Voice", prompt)
        self.assertIn("hộp thư", prompt)


class WriterTest(unittest.TestCase):
    def test_request_shape(self):
        req = build_request(Brain(profile="x"), "topic", "facebook")
        self.assertEqual(req["model"], "claude-opus-5-5")
        self.assertEqual(req["thinking"], {"type": "adaptive"})
        self.assertIn("topic", req["messages"][0]["content"])


class QueueTest(unittest.TestCase):
    def test_add_approve_due(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "q.csv"
            post = queue.add(path, "facebook", "2026-01-01 08:00", "Xin chào\ndòng 2")
            self.assertEqual(post.id, "1")
            posts = queue.load(path)
            self.assertFalse(posts[0].due(datetime(2026, 1, 2)))  # still a draft
            posts[0].status = "approved"
            queue.save(path, posts)
            self.assertTrue(queue.load(path)[0].due(datetime(2026, 1, 2)))
            self.assertEqual(queue.load(path)[0].text, "Xin chào\ndòng 2")

    def test_example_queue_loads(self):
        posts = queue.load(EXAMPLE_BRAIN.parent / "queue.csv")
        self.assertEqual(posts[0].status, "draft")


class PublisherTest(unittest.TestCase):
    def test_dry_run_does_not_post(self):
        self.assertTrue(publishers.publish("facebook", "hi").startswith("[dry-run]"))

    def test_unknown_platform(self):
        with self.assertRaises(publishers.PublishError):
            publishers.publish("myspace", "hi")


if __name__ == "__main__":
    unittest.main()
