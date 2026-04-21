"""
Testes unitários para core/logger_config.py.

Cobre:
- Chamada com nível padrão (INFO)
- Chamada com níveis alternativos (DEBUG, WARNING, ERROR)
- Idempotência (múltiplas chamadas não devem lançar exceção)
- Criação do diretório de logs
"""

import pytest
from pathlib import Path
from core.logger_config import setup_logger


class TestSetupLogger:
    """Testa o comportamento da função setup_logger."""

    def test_default_level_does_not_raise(self):
        """Chamada sem argumentos (INFO) não deve lançar nenhuma exceção."""
        setup_logger()

    def test_debug_level_does_not_raise(self):
        """Nível DEBUG deve ser aceito sem erro."""
        setup_logger("DEBUG")

    def test_warning_level_does_not_raise(self):
        """Nível WARNING deve ser aceito sem erro."""
        setup_logger("WARNING")

    def test_error_level_does_not_raise(self):
        """Nível ERROR deve ser aceito sem erro."""
        setup_logger("ERROR")

    def test_idempotent_multiple_calls(self):
        """Chamar setup_logger várias vezes não deve acumular erros."""
        setup_logger()
        setup_logger("DEBUG")
        setup_logger()

    def test_log_directory_exists_after_setup(self):
        """O diretório logs/ deve existir após a configuração do logger."""
        setup_logger()
        log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        assert log_dir.exists(), f"Diretório de logs não encontrado: {log_dir}"

    def test_log_file_is_created(self):
        """O arquivo monitor_log.txt deve existir após a configuração."""
        setup_logger()
        log_file = Path(__file__).resolve().parent.parent.parent / "logs" / "monitor_log.txt"
        assert log_file.exists(), f"Arquivo de log não encontrado: {log_file}"
