import os
import tempfile
import shutil
import pytest
from src.backup_service import load_env_vars, perform_backup

class TestBackupService:
    def setup_method(self):
        # Set up temporary directories for testing
        self.source_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        # Create a test file in source
        with open(os.path.join(self.source_dir, 'test.txt'), 'w') as f:
            f.write('test content')

    def teardown_method(self):
        # Clean up temporary directories
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.dest_dir)

    def test_load_env_vars_defaults(self):
        # Test loading default environment variables
        source, dest, compress, email_to, email_from, smtp_server, smtp_port, smtp_user, smtp_pass = load_env_vars()
        assert source == '/home/user/documents'
        assert dest == '/backup/documents'
        assert compress is False
        # Add more assertions as needed

    def test_perform_backup(self):
        # Test the backup function (mock rsync if needed, but for simplicity, assume rsync is available)
        # This is a basic test; in a real scenario, you might mock subprocess
        try:
            perform_backup(self.source_dir, self.dest_dir, False)
            # Check if backup directory was created
            backup_dirs = [d for d in os.listdir(self.dest_dir) if d.startswith('backup_')]
            assert len(backup_dirs) > 0
        except Exception as e:
            pytest.fail(f"Backup failed: {e}")