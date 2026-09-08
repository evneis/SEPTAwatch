# Suggested next steps: SEPTAwatch usability

The app currently launches a branded welcome window. The items below are ordered by how much they would improve day-to-day use, not by engineering size.

## 1. Show real arrivals instead of a splash screen

The `vibecode-api` branch already had a Regional Rail search UI (`from` / `to` stations, result count, auto-refresh) and a `modules/api.py` client against SEPTA's NextToArrive / TrainView / Arrivals endpoints. Revive that as the home screen.

Usability details that the old UI still needed:

- **Parse the real field names.** NextToArrive typically returns `orig_train`, `orig_line`, `orig_departure_time`, `orig_delay`, and similar `term_*` keys. The old formatter looked for `train_id` / `origin` / `destination`, so every row could show "Unknown".
- **Do not hide network failures as "no trains found."** The old client caught exceptions, printed them to the console, and returned `[]`. The GUI then looked empty. Surface HTTP errors, timeouts, and JSON errors in the status bar.
- **Give the search button a loading state** and disable station combos while a request is in flight so double-clicks do not spawn overlapping threads.

## 2. Replace the dump of text with a scannable table

A commute app is used at a glance. A `QTableWidget` (or `QTableView`) with columns such as train, line, departs, arrives, delay, and status is much easier to scan than a `QTextEdit` blob. Color delays (on time / late / cancelled) and keep the last-updated time visible.

## 3. Let people pick stations the way they actually remember them

A hardcoded dozen-station combo box will always feel incomplete.

- Load the full Regional Rail station list (SEPTA publishes this via GTFS `stops.txt` and the locations API).
- Make the fields searchable / type-ahead, including aliases ("30th", "Jefferson" vs "Market East").
- Swap origin and destination with one control.
- Remember the last route (and a short list of favorites) in `QSettings` so the app opens on the commute, not on a demo pair of Center City stops.

## 4. Cover the rest of the trip, not only Regional Rail

Most SEPTA riders mix modes. After rail arrivals work:

- **Bus and trolley:** TransitView by route, plus stop-level predictions where the JSON APIs or GTFS-RT trip updates are reliable.
- **Service alerts and detours** on the same screen as the selected route, with a badge on the window or tray icon when something is disrupted.
- **Elevator outages** for wheelchair / luggage trips through Center City.

Keep each mode on its own tab or page, but share the same "favorites + alerts" chrome so people do not relearn the app.

## 5. Make it a glanceable companion, not a window you hunt for

Once there is live data:

- Optional **always-on-top** compact view (next 1–3 trips only).
- **System tray** with the next train time in the tooltip, plus a click to show the full window.
- Configurable auto-refresh (15 / 30 / 60s) that pauses when the window is hidden, with a visible countdown.
- Persist window size, position, and compact vs full layout.

## 6. First-run and empty states

New users currently get "Welcome to SEPTAwatch!" with no next action.

- First launch: pick a home station or a saved trip in one short dialog.
- Empty / overnight / API-down states should say what happened and what to do ("No more trains tonight", "SEPTA did not respond — retry").
- Offline: show the last successful result with a stale timestamp rather than a blank pane.

## 7. Keyboard, contrast, and small-screen use

- Tab order through station fields → search → results.
- Shortcuts for refresh, swap stations, and quit (`Ctrl+Q` is already wired).
- Check the Fusion palette in both light and dark system themes; delay colors must still meet contrast on each.
- The current auto-scaling title font is a demo. Once there is real content, use a normal heading size and let the results table take the space.

## 8. Packaging that matches how people will install it

The build scripts now share `SEPTAwatch.spec`, but a first-time user still needs Python and PyInstaller.

- Document a one-click Windows installer (Inno Setup / WiX) that places a Start Menu shortcut and the logo.
- On Linux, a `.desktop` file and optional Flatpak/AppImage would avoid `chmod +x dist/SEPTAwatch`.
- Sign the Windows binary if you distribute outside GitHub Releases.

## Suggested sequence

1. Restore and correct the API client + table UI for one Regional Rail trip.
2. Persist last trip and favorites.
3. Add alerts for that trip.
4. Compact / tray glance view.
5. Bus and trolley using the same favorites model.

That order gets a useful commute tool on screen before expanding coverage.
