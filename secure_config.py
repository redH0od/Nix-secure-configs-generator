PACKAGES = {
    "Сеть и утилиты": [
        "curl", "wget", "netcat-gnu", "ipcalc",
        "whois", "dig", "traceroute", "iperf3", "tcpdump",
        "rsync", "aria2",
    ],
    "Редакторы": [
        "vim", "neovim", "emacs-nox", "nano", "helix",
    ],
    "Системные утилиты": [
        "htop", "btop", "tmux", "screen",
        "file", "unzip", "zip", "p7zip", "tree",
        "fd", "ripgrep", "fzf", "jq", "yq",
        "lsof", "strace", "ncdu", "duf", "bat",
        "eza", "zoxide", "tldr",
    ],
    "Безопасность": [
        "lynis", "tripwire", "tshark", "nmap",
        "openssl", "gnupg", "age", "sops",
        "aide",
    ],
    "Разработка": [
        "git", "gcc", "gnumake", "python3", "nodejs",
        "docker", "docker-compose", "ansible",
        "terraform", "kubectl",
    ],
    "Мониторинг и логи": [
        "prometheus", "grafana", "loki",
        "netdata", "glances", "logrotate",
    ],
    "Оболочки и окружение": [
        "bash", "zsh", "fish", "starship",
        "direnv", "nix-direnv",
    ],
}


SECURITY_OPTIONS = {
    "Антивирус ClamAV": """\
  services.clamav = {
    daemon.enable = true;
    updater.enable = true;
  };""",

    "Firewall": """\
  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ $tcp_ports ];
    allowedUDPPorts = [ $udp_ports ];
  };""",

    "Fail2ban": """\
  services.fail2ban = {
    enable = true;
    bantime = "$bantime";
    maxretry = 5;
    ignoreIP = [ "127.0.0.0/8" "10.0.0.0/8" "172.16.0.0/12" "192.168.0.0/16" ];
    jails.DEFAULT.settings.findtime = "$findtime";
    jails.sshd.settings = {
      filter = "sshd";
      maxretry = 5;
    };
  };""",

    "AppArmor (ограничение программ)": """\
  security.apparmor = {
    enable = true;
    policies."openssh-server" = {
      state = "enforce";
      profile = ''
        #include <tunables/global>
        $${pkgs.openssh}/bin/sshd {
          #include <abstractions/base>
          #include <abstractions/nameservice>
          network inet stream,
          network inet6 stream,
          capability net_bind_service,
          capability setgid,
          capability setuid,
          /etc/ssh/ r,
          /etc/ssh/** r,
          /home/*/.ssh/authorized_keys r,
          /home/*/.ssh/authorized_keys2 r,
          /run/sshd.pid rw,
          $${pkgs.openssh}/bin/sshd mr,
        }
      '';
    };
  };""",

    "SSH только с ключами": """\
  services.openssh.settings = {
    PasswordAuthentication = false;
    KbdInteractiveAuthentication = false;
    PermitRootLogin = "no";
    X11Forwarding = false;
    UseDns = false;
  };""",

    "Защита от сетевых атак (SYN, IP-подделка)": {
        "net.ipv4.tcp_syncookies": 1,
        "net.ipv4.conf.all.rp_filter": 1,
        "net.ipv4.conf.default.rp_filter": 1,
        "kernel.kptr_restrict": 2,
        "kernel.dmesg_restrict": 1,
    },

    "Защита памяти и процессов (ASLR, ptrace, BPF)": {
        "kernel.randomize_va_space": 2,
        "kernel.yama.ptrace_scope": 1,
        "kernel.unprivileged_bpf_disabled": 1,
        "net.core.bpf_jit_harden": 2,
        "user.max_user_namespaces": 0,
    },

    "tmpfs с защитой": """\
  boot.tmp.useTmpfs = true;
  boot.tmp.tmpfsSize = "2G";

  fileSystems."/var/tmp" = {
    device = "none";
    fsType = "tmpfs";
    options = [ "noexec" "nosuid" "nodev" "size=1G" ];
  };

  systemd.mounts = [
    {
      where = "/dev/shm";
      what = "tmpfs";
      type = "tmpfs";
      options = "nodev,nosuid,noexec,size=2G";
      before = [ "sysinit.target" ];
    }
  ];""",

    "Ограничения сервисов systemd": """\
  systemd.services = {
    NetworkManager.serviceConfig = {
      PrivateTmp = true;
      NoNewPrivileges = true;
    };
    sshd.serviceConfig = {
      PrivateTmp = true;
      ProtectSystem = "strict";
      PrivateDevices = true;
      NoNewPrivileges = true;
      RestrictSUIDSGID = true;
    };
  };""",

    "Отключить автоматическое монтирование USB": """\
  services.udisks2.enable = false;""",

    "Отключить сетевые Zeroconf-сервисы (AirPlay, mDNS)": """\
  services.avahi.enable = false;""",
}

DESKTOP_OPTIONS = {
    "Без графики (Minimal)": "",

    "GNOME": """\
  services.xserver.enable = true;
  services.displayManager.gdm.enable = true;
  services.desktopManager.gnome.enable = true;""",

    "KDE Plasma 6": """\
  services.xserver.enable = true;
  services.desktopManager.plasma6.enable = true;
  services.displayManager.sddm.enable = true;
  services.displayManager.sddm.wayland.enable = true;""",

    "XFCE": """\
  services.xserver.enable = true;
  services.xserver.desktopManager.xfce.enable = true;
  services.xserver.desktopManager.xterm.enable = false;
  services.displayManager.lightdm.enable = true;""",

    "i3 (tiling WM)": """\
  services.xserver.enable = true;
  services.xserver.windowManager.i3.enable = true;
  services.displayManager.lightdm.enable = true;""",

    "Hyprland (Wayland)": """\
  programs.hyprland.enable = true;
  programs.hyprland.xwayland.enable = true;
  xdg.portal.enable = true;
  xdg.portal.extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
  environment.sessionVariables.NIXOS_OZONE_WL = "1";""",

    "COSMIC (экспериментально)": """\
  services.displayManager.cosmic-greeter.enable = true;
  services.desktopManager.cosmic.enable = true;""",
}

GUI_PACKAGES = {
    "Браузеры": ["firefox", "chromium", "tor-browser-bundle-bin"],
    "Мультимедиа": ["vlc", "mpv", "gimp", "audacity", "obs-studio"],
    "Графические утилиты": ["kitty", "alacritty", "pcmanfm", "feh", "flameshot"],
}

NIX_CONFIG_TEMPLATE = """\
{ config, pkgs, lib, ... }:

{
  networking.hostName = "$hostname";
  time.timeZone = "$timezone";

  services.openssh = {
    enable = true;
    settings.PermitRootLogin = "no";
  };

  environment.systemPackages = with pkgs; [
$nix_packages
  ];

$desktop_config
$generated_config
  users.users.$username = {
    isNormalUser = true;
    description = "$user_description";
    extraGroups = [ "wheel" ];
$user_extra
  };

  security.sudo.wheelNeedsPassword = true;

  system.stateVersion = "$state_version";
}
"""
