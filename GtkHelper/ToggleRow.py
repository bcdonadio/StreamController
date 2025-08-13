import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GObject

class ToggleRow(Adw.ActionRow):
    def __init__(self,
                 toggles: list[Adw.Toggle],
                 active_toggle: int,
                 title: str,
                 subtitle: str,
                 can_shrink: bool,
                 homogeneous: bool,
                 active: bool):
        super().__init__(title=title, subtitle=subtitle)

        # Check if ToggleGroup is available (libadwaita 1.7+)
        try:
            self.toggle_group = Adw.ToggleGroup()
            self.toggle_group.set_can_shrink(can_shrink)
            self.toggle_group.set_homogeneous(homogeneous)
            self.toggle_group.set_active(active)
            self.toggle_group.set_valign(Gtk.Align.CENTER)
            self.using_toggle_group = True
        except AttributeError:
            # Fallback for libadwaita 1.6.6 (GNOME 48 runtime)
            self.toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            self.toggle_box.set_can_shrink(can_shrink)
            self.toggle_box.set_homogeneous(homogeneous)
            self.toggle_box.set_valign(Gtk.Align.CENTER)
            self.using_toggle_group = False
            self.toggle_group = self.toggle_box  # Use box as placeholder

        toggles = toggles or []
        active_index = active_toggle or 0
        self.populate(toggles, active_index)

        self.add_suffix(self.toggle_group)

    def get_toggles(self):
        if self.using_toggle_group:
            return self.toggle_group.get_toggles()
        else:
            return self.toggle_box.get_children()

    def get_n_toggles(self):
        if self.using_toggle_group:
            return self.toggle_group.get_n_toggles()
        else:
            return len(self.toggle_box.get_children())

    def get_toggle_by_name(self, name: str):
        if self.using_toggle_group:
            return self.toggle_group.get_toggle_by_name(name)
        else:
            for child in self.toggle_box.get_children():
                if child.get_name() == name:
                    return child
            return None

    def get_toggle_at(self, index: int):
        if self.using_toggle_group:
            return self.toggle_group.get_toggle(index)
        else:
            children = self.toggle_box.get_children()
            if 0 <= index < len(children):
                return children[index]
            return None

    def get_active_toggle(self):
        if self.using_toggle_group:
            toggle_index = self.toggle_group.get_active()
            return self.toggle_group.get_toggle(toggle_index)
        else:
            for child in self.toggle_box.get_children():
                if isinstance(child, Gtk.ToggleButton) and child.get_active():
                    return child
            return None

    def get_active_index(self):
        if self.using_toggle_group:
            return self.toggle_group.get_active()
        else:
            for i, child in enumerate(self.toggle_box.get_children()):
                if isinstance(child, Gtk.ToggleButton) and child.get_active():
                    return i
            return -1

    def get_active_name(self):
        if self.using_toggle_group:
            return self.toggle_group.get_active_name()
        else:
            active = self.get_active_toggle()
            return active.get_name() if active else None

    def set_active_toggle(self, index: int):
        if self.using_toggle_group:
            self.toggle_group.set_active(index)
        else:
            children = self.toggle_box.get_children()
            if 0 <= index < len(children):
                children[index].set_active(True)

    def set_active_by_name(self, name: str):
        if self.using_toggle_group:
            self.toggle_group.set_active_name(name)
        else:
            for child in self.toggle_box.get_children():
                if child.get_name() == name:
                    child.set_active(True)
                    break

    def add_toggle(self, label = None, tooltip: str = None, icon_name: str = None, name: str = None, enabled: bool = True):
        if self.using_toggle_group:
            self.toggle_group.add(
                Adw.Toggle(label=label, tooltip=tooltip, icon_name=icon_name, name=name, enabled=enabled)
            )
        else:
            toggle = Gtk.ToggleButton(label=label)
            toggle.set_tooltip_text(tooltip or "")
            toggle.set_name(name or "")
            toggle.set_sensitive(enabled)
            self.toggle_box.append(toggle)

    def add_toggles(self, toggles: list[Adw.Toggle]):
        if self.using_toggle_group:
            for toggle in toggles:
                self.toggle_group.add(toggle)
        else:
            for toggle in toggles:
                self.add_toggle(
                    label=toggle.get_label(),
                    tooltip=toggle.get_tooltip_text(),
                    icon_name=toggle.get_icon_name(),
                    name=toggle.get_name(),
                    enabled=toggle.get_enabled()
                )

    def populate(self, toggles: list[Adw.Toggle], active_index: int):
        if self.using_toggle_group:
            self.toggle_group.remove_all()
            self.add_toggles(toggles)
            self.toggle_group.set_active(active_index)
        else:
            # Remove all children
            for child in self.toggle_box.get_children():
                self.toggle_box.remove(child)
            self.add_toggles(toggles)
            self.set_active_toggle(active_index)

    def add_custom_toggle(self, toggle: Adw.Toggle):
        if self.using_toggle_group:
            self.toggle_group.add(toggle)
        else:
            self.add_toggle(
                label=toggle.get_label(),
                tooltip=toggle.get_tooltip_text(),
                icon_name=toggle.get_icon_name(),
                name=toggle.get_name(),
                enabled=toggle.get_enabled()
            )

    def remove_toggle(self, toggle: Adw.Toggle):
        if self.using_toggle_group:
            self.toggle_group.remove(toggle)
        else:
            self.toggle_box.remove(toggle)

    def remove_at(self, index: int):
        if self.using_toggle_group:
            toggle = self.get_toggle_at(index)
            self.toggle_group.remove(toggle)
        else:
            toggle = self.get_toggle_at(index)
            if toggle:
                self.toggle_box.remove(toggle)

    def remove_with_name(self, name: str):
        if self.using_toggle_group:
            toggle = self.toggle_group.get_toggle_by_name(name)
            self.toggle_group.remove(toggle)
        else:
            toggle = self.get_toggle_by_name(name)
            if toggle:
                self.toggle_box.remove(toggle)

    def remove_all(self):
        if self.using_toggle_group:
            self.toggle_group.remove_all()
        else:
            for child in self.toggle_box.get_children():
                self.toggle_box.remove(child)
