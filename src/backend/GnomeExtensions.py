"""
Author: Core447
Year: 2024

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This programm comes with ABSOLUTELY NO WARRANTY!

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
try:
    import dbus as _dbus_module
except Exception:
    _dbus_module = None
from loguru import logger as log
import os

class GnomeExtensions:
    def __init__(self):
        self.bus = None
        self.proxy = None
        self.interface = None
        self.using_dbus_python = None
        self.connect_dbus()

    def connect_dbus(self) -> None:
        """
        Try dbus-python first (if available). If that fails, fall back to Gio.DBus
        and expose a small wrapper that provides ListExtensions() and
        InstallRemoteExtension(uuid) so the rest of the code can keep calling
        the same methods.
        Also log environment variables useful when debugging under Flatpak / the mcp-debugger.
        """
        # Helpful environment details for debugging Flatpak/dbus issues
        log.debug(f"DBUS_SESSION_BUS_ADDRESS={os.environ.get('DBUS_SESSION_BUS_ADDRESS')}")
        log.debug(f"XDG_RUNTIME_DIR={os.environ.get('XDG_RUNTIME_DIR')}")
        log.debug(f"FLATPAK_ID={os.environ.get('FLATPAK_ID')}")

        # First attempt: dbus-python (may not be available inside the Flatpak runtime)
        if _dbus_module is not None:
            try:
                self.bus = _dbus_module.SessionBus()
                self.proxy = self.bus.get_object("org.gnome.Shell", "/org/gnome/Shell")
                self.interface = _dbus_module.Interface(self.proxy, "org.gnome.Shell.Extensions")
                self.using_dbus_python = True
                log.info("Connected to D-Bus using dbus-python")
                return
            except Exception as e:
                log.error(f"Failed to connect using dbus-python: {e}")

        # Fallback: use Gio (recommended inside Flatpak / GLib event loop)
        try:
            import gi
            gi.require_version("Gio", "2.0")
            from gi.repository import Gio, GLib

            session_bus = Gio.bus_get_sync(Gio.BusType.SESSION)
            proxy = Gio.DBusProxy.new_sync(
                connection=session_bus,
                flags=Gio.DBusProxyFlags.DO_NOT_LOAD_PROPERTIES,
                info=None,
                name='org.gnome.Shell',
                object_path='/org/gnome/Shell',
                interface_name='org.gnome.Shell.Extensions',
                cancellable=None
            )

            class _GioInterfaceWrapper:
                def __init__(self, proxy):
                    self.proxy = proxy

                def ListExtensions(self):
                    # Call the method with no parameters
                    res = self.proxy.call_sync("ListExtensions", None, Gio.DBusCallFlags.NONE, -1, None)
                    if res is None:
                        return []
                    try:
                        r = res.unpack()
                    except Exception:
                        r = res
                    # Some return values are wrapped in a single-element tuple
                    if isinstance(r, tuple) and len(r) == 1:
                        r = r[0]
                    if isinstance(r, list):
                        return r
                    try:
                        return list(r)
                    except Exception:
                        return []

                def InstallRemoteExtension(self, uuid):
                    params = GLib.Variant("(s)", (uuid,))
                    res = self.proxy.call_sync("InstallRemoteExtension", params, Gio.DBusCallFlags.NONE, -1, None)
                    if res is None:
                        return False
                    try:
                        r = res.unpack()
                        if isinstance(r, tuple) and len(r) == 1:
                            r = r[0]
                        return r
                    except Exception:
                        return res

            self.bus = session_bus
            self.proxy = proxy
            self.interface = _GioInterfaceWrapper(proxy)
            self.using_dbus_python = False
            log.info("Connected to D-Bus using Gio.DBus")
            return
        except Exception as e:
            log.error(f"Failed to connect using Gio.DBus: {e}")

        # Both attempts failed — ensure attributes are None so callers can handle missing D-Bus
        self.bus = None
        self.proxy = None
        self.interface = None
        self.using_dbus_python = None

    def get_is_connected(self) -> bool:
        return None not in (self.bus, self.proxy, self.interface)

    def get_installed_extensions(self) -> list[str]:
        extensions: list[str] = []
        if not self.get_is_connected(): return extensions

        for extension in self.interface.ListExtensions():
            extensions.append(extension)
        return extensions

    def request_installation(self, uuid: str) -> bool:
        if not self.get_is_connected(): return False
        response = self.interface.InstallRemoteExtension(uuid)
        return True if response == "successful" else False
