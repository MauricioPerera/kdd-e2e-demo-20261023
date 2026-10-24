"""Execute real CI steps against independently frozen Git fixture snapshots."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'quality/product.json'
WORKFLOW = '.github/workflows/validate.yml'
EVIDENCE = 'docs/task-evidence/TASK-001-abb784d29a0fabd2e2c956218f6f45bb098a6867.json'


def step_body(name):
    workflow = (ROOT / WORKFLOW).read_text(encoding='utf-8')
    marker = '      - name: ' + name + '\n'
    if marker not in workflow:
        raise AssertionError('Required CI step is missing: ' + name)
    step = workflow.split(marker, 1)[1].split('      - name:', 1)[0]
    return textwrap.dedent(step.split('        run: |\n', 1)[1])


class ProductQualityCiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_temp = tempfile.TemporaryDirectory(prefix='kdd-quality-ci-base-')
        cls.base = Path(cls.base_temp.name) / 'project'
        cls.env = dict(os.environ, PYTHONUTF8='1', GIT_CONFIG_NOSYSTEM='1',
                       GIT_CONFIG_GLOBAL=os.devnull)
        for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR'):
            cls.env.pop(key, None)
        cls.command(['git', 'clone', '-q', '--no-hardlinks', str(ROOT), str(cls.base)])
        # Overlay the draft configuration under test, never local logs/tokens.
        names = cls.command(['git', '-C', str(ROOT), 'ls-files', '--cached',
                             '--others', '--exclude-standard', '-z']).stdout.split('\0')
        for name in filter(None, names):
            source, target = ROOT / name, cls.base / name
            if source.is_file() and (not target.is_file() or source.read_bytes() != target.read_bytes()):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        for key, value in (('user.name', 'Quality fixture reviewer'),
                           ('user.email', 'reviewer@example.test'),
                           ('core.autocrlf', 'false'), ('commit.gpgsign', 'false')):
            cls.command(['git', '-C', str(cls.base), 'config', key, value])
        cls.command(['git', '-C', str(cls.base), 'add', '.'])
        cls.command(['git', '-C', str(cls.base), 'commit', '--allow-empty', '-qm',
                     'Reviewed configuration fixture; not a real project approval'])
        cls.approved = cls.command(['git', '-C', str(cls.base), 'rev-parse', 'HEAD']).stdout.strip()

    @classmethod
    def tearDownClass(cls):
        cls.base_temp.cleanup()

    @classmethod
    def command(cls, args, cwd=None, env=None, check=True):
        return subprocess.run(args, cwd=cwd, env=env or cls.env, capture_output=True,
                              text=True, encoding='utf-8', errors='replace',
                              timeout=90, check=check)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kdd-quality-ci-case-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.command(['git', 'clone', '-q', '--shared', str(self.base), str(self.root)])
        self.git('config', 'user.name', 'Quality fixture developer')
        self.git('config', 'user.email', 'developer@example.test')
        self.git('config', 'core.autocrlf', 'false')
        self.git('config', 'commit.gpgsign', 'false')

    def git(self, *args):
        return self.command(['git', *args], cwd=self.root).stdout.strip()

    def run_step(self, name='Approve project quality (when configured)', **overrides):
        env = dict(self.env, KDD_QUALITY_POLICY=POLICY,
                   KDD_QUALITY_APPROVED_REF=self.approved, KDD_REQUIRED_EVIDENCE='quality')
        env.update(overrides)
        return self.command([sys.executable, '-c', step_body(name)], cwd=self.root,
                            env=env, check=False)

    def assert_rejected(self, result, reason):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(reason, result.stdout + result.stderr)
        self.assertNotIn('PASS quality:', result.stdout)

    def test_native_defaults_and_existing_validation_are_preserved(self):
        text = (ROOT / WORKFLOW).read_text(encoding='utf-8')
        self.assertIn("quality_policy_path:\n        type: string\n        default: 'quality/product.json'", text)
        self.assertEqual(text.count("KDD_QUALITY_POLICY: ${{ inputs.quality_policy_path || 'quality/product.json' }}"), 2)
        self.assertIn("KDD_REQUIRED_EVIDENCE: ${{ inputs.required_evidence || 'quality' }}", text)
        self.assertIn('vars.KDD_QUALITY_APPROVED_REF', text)
        self.assertLess(text.index('- name: Check product quality approval configuration'),
                        text.index("- name: Run each contract's test_command"))
        self.assertEqual(text.count('os: [ubuntu-latest, windows-latest]'), 2)
        self.assertEqual(text.count('run: python -m unittest discover -s tests -p "test_*.py"'), 2)
        self.assertIn('- name: Validate Git task snapshots and transitions', text)
        self.assertIn('KDD_QUALITY_OUTCOME: ${{ steps.quality.outcome }}', text)
        self.assertNotIn('continue-on-error:', text)

    def test_policy_keeps_protections_and_pins_closed_task_artifacts(self):
        policy = json.loads((ROOT / POLICY).read_text(encoding='utf-8'))
        previous = json.loads(self.command(['git', '-C', str(ROOT), 'show',
            '64ccf3a166b6822df623ba97ae7e0a4c638dabbc:' + POLICY]).stdout)
        self.assertTrue(set(previous['protected']).issubset(policy['protected']))
        for name in (WORKFLOW, 'scripts/verify_quality.py', 'tests/test_product_quality_ci.py',
                     'knowledge/contracts/product-quality-ci.md', 'knowledge/product-quality-ci.md',
                     'knowledge/tasks/TASK-001.md', EVIDENCE):
            self.assertIn(name, policy['protected'])
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertEqual(policy['checks'], previous['checks'])
        self.assertEqual(policy['required_kinds'], ['functional', 'adversarial', 'ui'])
        self.assertNotIn('knowledge/tasks/TASK-001.md', policy['pm'])
        self.assertEqual(policy['implementation'], ['src/greeting.py'])
        self.assertFalse(any(char in name for group in ('protected', 'pm', 'implementation')
                             for name in policy[group] for char in '*?[]'))

    def test_configuration_requires_policy_and_full_ancestral_sha(self):
        name = 'Check product quality approval configuration'
        self.assertEqual(self.run_step(name).returncode, 0)
        for ref in ('', 'HEAD', 'main', 'f' * 40):
            with self.subTest(ref=ref):
                self.assertNotEqual(self.run_step(name, KDD_QUALITY_APPROVED_REF=ref).returncode, 0)
        tree = self.git('rev-parse', 'HEAD^{tree}')
        orphan = self.git('commit-tree', tree, '-m', 'unrelated fixture approval')
        self.assertNotEqual(self.run_step(name, KDD_QUALITY_APPROVED_REF=orphan).returncode, 0)
        (self.root / POLICY).unlink()
        self.assertNotEqual(self.run_step(name).returncode, 0)

    def test_real_closed_project_runs_all_product_checks_twice(self):
        result = self.run_step()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS quality: integrity, perimeter and all checks verified twice', result.stdout)
        for check, kind in (('contracts', 'structural'), ('functional', 'functional'),
                            ('adversarial', 'adversarial'), ('cli', 'ui')):
            for iteration in (1, 2):
                self.assertIn('RUN %s/2 %s [%s]' % (iteration, check, kind), result.stdout)
        self.assertNotIn('SKIP: no project quality policy', result.stdout)
        journal = self.command([sys.executable, 'scripts/validate_tasks.py', '--base-ref',
            'b444b8e967a92b03c729401ceaafd8b1190639d8', '--head-ref', 'HEAD'], cwd=self.root)
        self.assertIn('Task validation: 0 error(s)', journal.stdout)

    def test_missing_reference_cannot_skip_present_product(self):
        self.assert_rejected(self.run_step(KDD_QUALITY_APPROVED_REF=''), 'explicitly approved reference')

    def test_current_runner_cannot_forge_a_success(self):
        (self.root / 'scripts/verify_quality.py').write_text("print('PASS quality: FAKE CURRENT RUNNER')\n")
        result = self.run_step()
        self.assert_rejected(result, 'Protected file changed: scripts/verify_quality.py')
        self.assertNotIn('FAKE CURRENT RUNNER', result.stdout)

    def test_policy_and_oracle_tampering_are_rejected(self):
        for name in (POLICY, 'tests/test_greeting.py'):
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.write_bytes(original + b'\n# unauthorized change\n')
                self.assert_rejected(self.run_step(), 'Protected file changed: ' + name)
                path.write_bytes(original)

    def test_committed_outside_code_and_unknown_evidence_are_rejected(self):
        for name in ('src/undeclared.py', 'docs/task-evidence/TASK-999-' + 'a' * 40 + '.json'):
            with self.subTest(name=name):
                path = self.root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('unexpected = True\n')
                self.git('add', name)
                self.git('commit', '-qm', 'Unapproved fixture artifact')
                self.assert_rejected(self.run_step(), 'Outside approved perimeter: ' + name)
                self.git('reset', '--hard', self.approved)

    def test_closed_evidence_is_immutable(self):
        (self.root / EVIDENCE).write_text('{}\n')
        self.assert_rejected(self.run_step(), 'Protected file changed: ' + EVIDENCE)

    def test_product_failure_never_reports_global_pass(self):
        (self.root / 'src/greeting.py').write_text('def greet(name):\n    return "wrong"\n')
        self.assert_rejected(self.run_step(), 'Check failed: functional')

    def test_optional_summary_reports_real_quality_outcome(self):
        env = dict(self.env, KDD_QUALITY_POLICY=POLICY,
                   KDD_QUALITY_OUTCOME='success', KDD_REQUIRED_EVIDENCE='quality')
        result = self.command([sys.executable, 'scripts/optional_evidence.py', 'summary',
                               '--layers', 'quality'], cwd=self.root, env=env)
        self.assertIn('PASS [quality] quality/product.json', result.stdout.replace('\\', '/'))
        self.assertNotIn('SKIP [quality]', result.stdout)
        env['KDD_QUALITY_OUTCOME'] = 'failure'
        failed = self.command([sys.executable, 'scripts/optional_evidence.py', 'summary',
                               '--layers', 'quality'], cwd=self.root, env=env, check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('FAIL [quality]', failed.stdout)


if __name__ == '__main__':
    unittest.main()
