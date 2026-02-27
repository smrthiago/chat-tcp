"""
Interface CLI colorida do chat — formatação de mensagens com colorama.
"""
import sys
from datetime import datetime

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    _COLORAMA = True
except ImportError:
    _COLORAMA = False

    # Stubs para quando colorama não está disponível
    class _NoColor:
        def __getattr__(self, _): return ""

    class _NoStyle:
        def __getattr__(self, _): return ""

    Fore = _NoColor()
    Style = _NoStyle()


# ── Paleta de cores ──────────────────────────────────────────────────────────
COLOR_OWN   = Fore.CYAN
COLOR_OTHER = Fore.GREEN
COLOR_DM    = Fore.MAGENTA
COLOR_SYS   = Fore.YELLOW
COLOR_ERR   = Fore.RED
COLOR_INFO  = Fore.WHITE
COLOR_DIM   = Style.DIM
RESET       = Style.RESET_ALL


class ChatUI:
    """
    Interface de linha de comando para o chat.
    Centraliza toda a formatação e exibição de mensagens.
    """

    @staticmethod
    def print_welcome(username: str, users_online: list) -> None:
        """Exibe banner de boas-vindas ao entrar no chat."""
        print("\n" + "═" * 60)
        print(f"  🔌 Chat TCP/IP  •  Conectado como {COLOR_OWN}{username}{RESET}")
        print(f"  🔐 Criptografia Fernet (AES-128) ativa")
        print("═" * 60)

        if users_online:
            print(f"{COLOR_SYS}  Usuários online: {', '.join(users_online)}{RESET}")
        else:
            print(f"{COLOR_DIM}  Você é o primeiro a entrar!{RESET}")

        ChatUI.print_help()
        print()

    @staticmethod
    def print_help() -> None:
        """Exibe lista de comandos disponíveis."""
        print(f"\n{COLOR_DIM}  Comandos: /users  /dm <user> <msg>  /help  /quit{RESET}")

    @staticmethod
    def print_message(sender: str, content: str,
                      own_username: str, timestamp: str = None,
                      is_dm: bool = False) -> None:
        """
        Exibe mensagem de chat formatada.

        Args:
            sender:       Username de quem enviou.
            content:      Texto da mensagem em claro.
            own_username: Username do usuário local (para colorir diferente).
            timestamp:    ISO 8601 opcional.
            is_dm:        True se é mensagem direta.
        """
        time_str = _format_time(timestamp)
        prefix = "💬" if not is_dm else "🔮"

        if sender == own_username:
            color = COLOR_OWN
            label = "Você"
        elif is_dm:
            color = COLOR_DM
            label = f"DM de {sender}"
        else:
            color = COLOR_OTHER
            label = sender

        print(f"\r{COLOR_DIM}[{time_str}]{RESET} {prefix} {color}{label}:{RESET} {content}")

    @staticmethod
    def print_system(message: str) -> None:
        """Exibe notificação do sistema (entrada/saída de usuário)."""
        print(f"\r{COLOR_SYS}  ℹ  {message}{RESET}")

    @staticmethod
    def print_error(message: str) -> None:
        """Exibe mensagem de erro."""
        print(f"\r{COLOR_ERR}  ✗  {message}{RESET}")

    @staticmethod
    def print_info(message: str) -> None:
        """Exibe informação genérica."""
        print(f"\r{COLOR_INFO}  •  {message}{RESET}")

    @staticmethod
    def print_user_list(users: list) -> None:
        """Exibe lista de usuários online."""
        print(f"\n{COLOR_SYS}  👥 Usuários online ({len(users)}):{RESET}")
        for user in users:
            username = user.get("username", user) if isinstance(user, dict) else user
            connected_at = user.get("connected_at", "") if isinstance(user, dict) else ""
            time_str = _format_time(connected_at) if connected_at else ""
            suffix = f" {COLOR_DIM}(desde {time_str}){RESET}" if time_str else ""
            print(f"    • {COLOR_OTHER}{username}{RESET}{suffix}")
        print()

    @staticmethod
    def print_connecting(host: str, port: int) -> None:
        """Indica tentativa de conexão."""
        print(f"\n{COLOR_INFO}  Conectando a {host}:{port}...{RESET}")

    @staticmethod
    def print_reconnecting(attempt: int, max_attempts: int, delay: float) -> None:
        """Indica tentativa de reconexão."""
        print(
            f"\r{COLOR_SYS}  ↻  Reconectando [{attempt}/{max_attempts}] "
            f"em {delay:.0f}s...{RESET}"
        )

    @staticmethod
    def print_disconnected() -> None:
        """Indica desconexão do servidor."""
        print(f"\n{COLOR_ERR}  ✗  Desconectado do servidor.{RESET}\n")

    @staticmethod
    def prompt(username: str) -> str:
        """Renderiza o prompt de input."""
        return f"{COLOR_OWN}{username}{RESET} > "


def _format_time(iso_str: str) -> str:
    """Formata ISO 8601 para HH:MM."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except Exception:
        return datetime.now().strftime("%H:%M")
