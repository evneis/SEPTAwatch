# Suggested next steps: SEPTAwatch usability

Live SEPTA JSON APIs are now wired into tabbed tables (alerts, Regional Rail, arrivals, next-to-arrive, bus/trolley, Metro, elevators). Network errors show in the status bar. The items below are what is still missing for day-to-day commute use.

## 1. Let people pick stations the way they actually remember them

The Regional Rail combos now use the official station list plus aliases ("Jefferson" → `Market East`), but they still do not persist.

- Make the fields searchable / type-ahead.
- Swap origin and destination with one control.
- Remember the last route (and a short list of favorites) in `QSettings` so the app opens on the commute, not on a demo pair of Center City stops.

## 2. Tie alerts to the trip you care about

Alerts and elevator outages are on their own tabs. Next:

- Show service alerts and detours on the same screen as the selected route, with a badge on the window or tray icon when something is disrupted.
- Filter alerts by the current from/to stations or bus route instead of a raw `route_id`.

## 3. Make it a glanceable companion, not a window you hunt for

- Optional **always-on-top** compact view (next 1–3 trips only).
- **System tray** with the next train time in the tooltip, plus a click to show the full window.
- Configurable auto-refresh (15 / 30 / 60s) that pauses when the window is hidden, with a visible countdown.
- Persist window size, position, and compact vs full layout.

## 4. First-run and empty states

- First launch: pick a home station or a saved trip in one short dialog.
- Empty / overnight / API-down states should say what happened and what to do ("No more trains tonight", "SEPTA did not respond — retry").
- Offline: show the last successful result with a stale timestamp rather than a blank pane.

## 5. Keyboard, contrast, and small-screen use

- Tab order through station fields → search → results.
- Shortcuts for refresh (`F5` / File → Refresh), swap stations, and quit (`Ctrl+Q`).
- Check the Fusion palette in both light and dark system themes; delay colors must still meet contrast on each.

## 6. Packaging that matches how people will install it

The build scripts now share `SEPTAwatch.spec`, but a first-time user still needs Python and PyInstaller.

- Document a one-click Windows installer (Inno Setup / WiX) that places a Start Menu shortcut and the logo.
- On Linux, a `.desktop` file and optional Flatpak/AppImage would avoid `chmod +x dist/SEPTAwatch`.
- Sign the Windows binary if you distribute outside GitHub Releases.

## Suggested sequence

1. Persist last trip and favorites.
2. Surface alerts for the selected trip on the same screen.
3. Compact / tray glance view.
4. Stop-level bus/trolley predictions using the same favorites model.
