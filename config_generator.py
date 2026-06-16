import string
from security_config import SECURITY_OPTIONS, DESKTOP_OPTIONS, NIX_CONFIG_TEMPLATE


def _render_packages(packages: list[str]) -> str:
    packages = [p.strip() for p in packages if p and p.strip()]
    if not packages:
        return "    # Пакеты не выбраны."
    return "\n".join(f"    {p}" for p in packages)


def _render_desktop(desktop: str) -> str:
    if not desktop or desktop == "Без графики (Minimal)":
        return ""
    block = DESKTOP_OPTIONS.get(desktop, "")
    return block + "\n" if block else ""


def _render_security_blocks(selected_options: list[str], user_data: dict) -> str:
    blocks: list[str] = []
    merged_sysctl: dict[str, int] = {}

    for option in selected_options:
        block = SECURITY_OPTIONS.get(option)
        if block is None:
            continue

        if isinstance(block, dict):
            merged_sysctl.update(block)
            continue

        if option == "Firewall":
            tcp = " ".join(str(p) for p in user_data.get("tcp_ports", []))
            udp = " ".join(str(p) for p in user_data.get("udp_ports", []))
            rendered = string.Template(block).substitute(tcp_ports=tcp, udp_ports=udp)

        elif option == "Fail2ban":
            rendered = string.Template(block).substitute(
                bantime=user_data.get("bantime", "1h"),
                findtime=user_data.get("findtime", "10m"),
            )

        else:
            rendered = string.Template(block).substitute()

        blocks.append(rendered)

    if merged_sysctl:
        lines = "\n".join(
            f'    "{key}" = {val};' for key, val in merged_sysctl.items()
        )
        blocks.append(f"  boot.kernel.sysctl = {{\n{lines}\n  }};")

    if not blocks:
        return "  # Дополнительные опции безопасности не выбраны.\n"

    return "\n\n".join(blocks) + "\n"


def _render_user_extra(ssh_keys: list[str], password: str) -> str:
    lines: list[str] = []

    if password:
        escaped = password.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'    initialPassword = "{escaped}";')

    keys = [
        k.strip()
        for k in ssh_keys
        if k and k.strip() and not k.strip().startswith("#")
    ]
    keys = list(dict.fromkeys(keys))

    if keys:
        formatted = "\n      ".join(f'"{k}"' for k in keys)
        lines.append(
            f"    openssh.authorizedKeys.keys = [\n      {formatted}\n    ];"
        )

    return "\n".join(lines)


def generate_config(data: dict) -> str:
    packages_str = _render_packages(data.get("packages", []))

    user_data = {
        "tcp_ports": data.get("tcp_ports", []),
        "udp_ports": data.get("udp_ports", []),
        "bantime": data.get("bantime", "1h"),
        "findtime": data.get("findtime", "10m"),
    }
    security_str = _render_security_blocks(data.get("security_options", []), user_data)
    desktop_str = _render_desktop(data.get("desktop", ""))
    user_extra_str = _render_user_extra(
        data.get("ssh_keys", []),
        data.get("password", ""),
    )

    result = string.Template(NIX_CONFIG_TEMPLATE).substitute(
        hostname=data.get("hostname", "nixos"),
        timezone=data.get("timezone", "UTC"),
        nix_packages=packages_str,
        generated_config=security_str,
        desktop_config=desktop_str,
        username=data.get("username", "user"),
        user_description=data.get("user_description", "User"),
        state_version=data.get("state_version", "26.05"),
        user_extra=user_extra_str,
    )

    return result
