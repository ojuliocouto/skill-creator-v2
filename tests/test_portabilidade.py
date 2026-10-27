"""Cross-platform tests: run every script the way Claude Code runs it on macOS, Linux and Windows.

Each test installs a copy of the skill under a fake home whose path has an accent and a space,
forces the console encoding to cp1252 (the Windows default) and feeds a SKILL.md saved with
a BOM, CRLF line endings and non-ASCII text.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FRONTMATTER_SKILL = (
    "---\r\n"
    "name: relatorio-acao\r\n"
    'description: "Gera relatório de ação com análise \u2014 emoji 🚀 e acentuação: configuração, versão."\r\n'
    "triggers:\r\n"
    "  - gerar relatório\r\n"
    "  - análise de ação\r\n"
    "---\r\n"
    "\r\n"
    "# Relatório de Ação 🚀\r\n"
    "\r\n"
    "## Passo 1\r\n"
    "Rodar o script.\r\n"
    "\r\n"
    "## Erros\r\n"
    "Se falhar, mostrar a mensagem de erro.\r\n"
)


class Portabilidade(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="skill creator ação "))
        self.home = self.tmp / "Usuário Teste"
        self.skills = self.home / ".claude" / "skills"
        self.install = self.skills / "skill-creator-v2"
        shutil.copytree(REPO, self.install, ignore=shutil.ignore_patterns(".git", "__pycache__", "tests"))
        other = self.skills / "relatorio-acao"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_bytes(b"\xef\xbb\xbf" + FRONTMATTER_SKILL.encode("utf-8"))
        self.env = dict(os.environ)
        self.env.update({"HOME": str(self.home), "USERPROFILE": str(self.home), "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_script(self, name, *args):
        cmd = [sys.executable, str(self.install / "scripts" / name), *args]
        proc = subprocess.run(cmd, env=self.env, capture_output=True, timeout=120)
        out = proc.stdout.decode("utf-8", errors="strict")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertEqual(proc.returncode, 0, f"{name} {args} exit {proc.returncode}\nstdout:\n{out}\nstderr:\n{err}")
        return out

    def test_extract_frontmatter_reads_bom_and_crlf(self):
        out = self.run_script("extract_frontmatter.py", str(self.skills / "relatorio-acao" / "SKILL.md"), "--json", "--body")
        data = json.loads(out)
        fm = data.get("frontmatter", data)
        self.assertEqual(fm["name"], "relatorio-acao")
        self.assertIn("🚀", fm["description"])
        self.assertNotIn("\r", json.dumps(data))

    def test_analyze_skills_finds_skill_under_accented_home(self):
        out = self.run_script("analyze_skills.py", "--search", "relatório")
        self.assertIn("relatorio-acao", out)
        self.run_script("analyze_skills.py", "--summary")

    def test_collision_check_prints_non_ascii(self):
        out = self.run_script("collision_check.py", "--description", "Gera relatório de ação com análise e configuração", "--triggers", "gerar relatório")
        self.assertIn("relatorio-acao", out)

    def test_scaffold_then_audit_with_html(self):
        target = self.skills / "nova-skill-teste"
        self.run_script("scaffold.py", "--name", "nova-skill-teste", "--category", "utility", "--description", "Converte vídeo em áudio com análise de configuração e versão", "--triggers", "converter vídeo", "extrair áudio", "--output", str(target))
        self.assertTrue((target / "SKILL.md").is_file())
        report = self.tmp / "relatório da auditoria.html"
        self.run_script("audit_skill.py", "--skill-path", str(target), "--html", str(report))
        self.assertTrue(report.is_file())
        self.assertIn("<html", report.read_text(encoding="utf-8").lower())

    def test_self_audit_passes(self):
        out = self.run_script("audit_skill.py", "--skill-path", str(self.install), "--json")
        result = json.loads(out)
        self.assertGreaterEqual(result["total_score"], 45)

    def test_trigger_eval_set_with_bom(self):
        eval_set = {
            "should_trigger": ["quero gerar relatório de ação"],
            "should_not_trigger": ["fazer café"],
        }
        path = self.tmp / "avaliação.json"
        path.write_bytes(b"\xef\xbb\xbf" + json.dumps(eval_set, ensure_ascii=False).encode("utf-8"))
        self.run_script("test_triggers.py", "--description", "Gera relatório de ação com análise", "--eval-set", str(path))


if __name__ == "__main__":
    unittest.main()
