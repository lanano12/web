"""Verify the boundary between private source tooling and the public artifact."""
import tempfile
import unittest
from pathlib import Path
from package_site import package, public_files, ROOT


class PublicationBoundary(unittest.TestCase):
    def test_only_explicit_public_files_are_exported(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            result = package(output, 'github')
            self.assertEqual(result, public_files())
            self.assertFalse((output / 'tools').exists())
            self.assertFalse((output / '.git').exists())
            self.assertFalse((output / 'package.json').exists())
            self.assertFalse((output / '_headers').exists())
            self.assertTrue((output / '.well-known/security.txt').is_file())

    def test_contaminated_artifact_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            (output / 'secret.env').write_text('synthetic test data')
            with self.assertRaisesRegex(ValueError, 'unexpected files'):
                package(output, 'github')

    def test_symlink_destination_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'output'
            outside = Path(folder) / 'outside'
            output.mkdir(); outside.mkdir()
            (output / 'assets').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                package(output, 'github')
            self.assertEqual(list(outside.iterdir()), [])

    def test_source_directory_cannot_be_used_as_output(self):
        with self.assertRaises(ValueError):
            package(ROOT, 'github')

    def test_cloudflare_artifact_has_the_required_http_policy(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            package(output, 'cloudflare')
            policy = (output / '_headers').read_text()
            self.assertIn("frame-ancestors 'none'", policy)
            self.assertIn('Strict-Transport-Security: max-age=31536000', policy)


if __name__ == '__main__':
    unittest.main()
