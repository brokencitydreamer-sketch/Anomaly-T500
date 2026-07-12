from collections import Counter
import re
import time
import difflib
import ast
import json
import io
import os
import sys
import signal
import tempfile
import subprocess
from dataclasses import dataclass
from typing import Optional

try:
    import resource
    HAS_RESOURCE_LIMITS = True
except ImportError:
    HAS_RESOURCE_LIMITS = False


class ExecutionTimeout(Exception):
    """Raised when an automation exceeds its allotted run time."""
    pass


LANGUAGE_RUNNERS = {
    'python': ('.py', [sys.executable, '{path}']),
    'bash': ('.sh', ['bash', '{path}']),
    'shell': ('.sh', ['bash', '{path}']),
    'node': ('.js', ['node', '{path}']),
    'javascript': ('.js', ['node', '{path}']),
}

DEFAULT_MEMORY_MB = {
    'python': 256,
    'bash': 256,
    'shell': 256,
    'node': 1280,
    'javascript': 1280,
}


@dataclass
class ExecutionResult:
    name: str
    success: bool
    stdout: str
    stderr: str
    error: Optional[str]
    duration: float


class Automation:
    """Tracks one automation/script: its version history and usage stats."""

    def __init__(self, name, code, tags=None, language='python'):
        self.name = name
        self.language = language
        self.versions = [{
            'code': code,
            'timestamp': time.time(),
            'note': 'initial version',
        }]
        self.tags = tags or []
        self.created = time.time()
        self.last_run = None
        self.run_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_duration = None
        self.avg_duration = None
        self.last_error = None
        self.deprecated = False
        self.replaced_by = None
        self.depends_on = set()

    @property
    def current_code(self):
        return self.versions[-1]['code']

    def update(self, new_code, note=""):
        diff = list(difflib.
