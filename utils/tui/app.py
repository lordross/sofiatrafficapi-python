#!/usr/bin/env python3
"""
Sofia Traffic TUI Application

A terminal user interface for viewing Sofia public transport information.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TabbedContent,
    TabPane,
)

from sofiaclient import SofiaClient


class DeparturesTab(Container):
    """Tab for displaying stop departures."""

    DEFAULT_CSS = """
    DeparturesTab {
        padding: 1;
    }

    DeparturesTab #controls {
        height: auto;
        margin-bottom: 1;
    }

    DeparturesTab #stop-input {
        width: 20;
        margin-right: 1;
    }

    DeparturesTab #search-btn {
        margin-right: 1;
    }

    DeparturesTab #status-label {
        margin-left: 2;
        color: $text-muted;
    }

    DeparturesTab #stop-name-label {
        margin-bottom: 1;
        text-style: bold;
        color: $secondary;
    }

    DeparturesTab DataTable {
        height: 1fr;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.client: SofiaClient | None = None
        self.current_stop_id: str = ""
        self.auto_refresh_task: asyncio.Task | None = None
        self.auto_refresh_enabled: bool = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="controls"):
            yield Input(placeholder="Stop ID (e.g., A1289)", id="stop-input")
            yield Button("Search", id="search-btn", variant="primary")
            yield Button("Refresh", id="refresh-btn", variant="default")
            yield Label("", id="status-label")
        yield Label("", id="stop-name-label")
        yield DataTable(id="departures-table")

    def on_mount(self) -> None:
        """Set up the departures table."""
        table = self.query_one("#departures-table", DataTable)
        table.add_columns(
            "Line", "Direction", "Scheduled", "Estimated", "Deviation", "Live"
        )
        table.cursor_type = "row"
        table.zebra_stripes = True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "search-btn":
            await self.search_departures()
        elif event.button.id == "refresh-btn":
            await self.refresh_departures()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input."""
        if event.input.id == "stop-input":
            await self.search_departures()

    async def search_departures(self) -> None:
        """Search for departures at the specified stop."""
        stop_input = self.query_one("#stop-input", Input)
        stop_id = stop_input.value.strip()

        if not stop_id:
            self.update_status("Please enter a stop ID")
            return

        self.current_stop_id = stop_id
        await self.refresh_departures()

        # Start auto-refresh
        self.auto_refresh_enabled = True
        self.start_auto_refresh()

    async def refresh_departures(self) -> None:
        """Refresh the departures display."""
        if not self.current_stop_id:
            return

        self.update_status("Loading...")

        try:
            app = self.app
            if not isinstance(app, SofiaTrafficApp):
                return

            client = await app.get_client()

            # Get stop name
            stop = client._static_parser._stops.get(self.current_stop_id)
            stop_name = stop.name if stop else "Unknown Stop"

            stop_label = self.query_one("#stop-name-label", Label)
            stop_label.update(f"{stop_name} ({self.current_stop_id})")

            # Get departures with real-time data from current time onwards
            current_time = datetime.now().strftime("%H:%M")
            departures = await client.departures_by_location(
                self.current_stop_id,
                arg_date=current_time,
                realtime=True,
            )

            # Update table
            table = self.query_one("#departures-table", DataTable)
            table.clear()

            if not departures:
                self.update_status("No departures found")
                return

            # Limit to 20 departures
            departures = departures[:20]

            for dep in departures:
                line = dep.line_name or dep.line_id
                if dep.transport_type:
                    line = f"{line} ({dep.transport_type.name})"

                direction = dep.headsign or "-"
                scheduled = dep.planned_time.strftime("%H:%M") if dep.planned_time else "-"
                estimated = dep.estimated_time.strftime("%H:%M") if dep.estimated_time else "-"

                deviation = "-"
                if dep.estimated_time and dep.delay_minutes is not None:
                    if dep.delay_minutes > 0:
                        deviation = f"+{dep.delay_minutes} min"
                    elif dep.delay_minutes < 0:
                        deviation = f"{dep.delay_minutes} min"
                    else:
                        deviation = "On time"

                live = "\u2713" if dep.estimated_time else "\u2717"

                table.add_row(line, direction, scheduled, estimated, deviation, live)

            self.update_status(f"Found {len(departures)} departures")

        except Exception as e:
            self.update_status(f"Error: {str(e)[:50]}")

    def update_status(self, message: str) -> None:
        """Update the status label."""
        label = self.query_one("#status-label", Label)
        label.update(message)

    def start_auto_refresh(self) -> None:
        """Start auto-refresh task."""
        if self.auto_refresh_task is None or self.auto_refresh_task.done():
            self.auto_refresh_task = asyncio.create_task(self._auto_refresh_loop())

    def stop_auto_refresh(self) -> None:
        """Stop auto-refresh task."""
        if self.auto_refresh_task and not self.auto_refresh_task.done():
            self.auto_refresh_task.cancel()

    async def _auto_refresh_loop(self) -> None:
        """Auto-refresh loop."""
        while self.auto_refresh_enabled:
            await asyncio.sleep(60)  # Refresh every 1 minute
            if self.auto_refresh_enabled and self.current_stop_id:
                await self.refresh_departures()


class SofiaTrafficApp(App):
    """Sofia Traffic TUI Application."""

    TITLE = "Sofia Traffic"
    SUB_TITLE = "Public Transport Information"

    CSS = """
    Screen {
        background: $surface;
    }

    TabbedContent {
        padding: 0 1;
    }

    TabPane {
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "focus_departures", "Departures"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._client: SofiaClient | None = None
        self._client_context = None

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Departures", id="departures-tab"):
                yield DeparturesTab()
        yield Footer()

    async def get_client(self) -> SofiaClient:
        """Get or create the Sofia client."""
        if self._client is None:
            self._client = SofiaClient("https://gtfs.sofiatraffic.bg/api/v1/")
            self._client_context = await self._client.__aenter__()
        return self._client

    async def on_unmount(self) -> None:
        """Clean up resources."""
        if self._client:
            await self._client.__aexit__(None, None, None)

    def action_refresh(self) -> None:
        """Refresh the current view."""
        departures_tab = self.query_one(DeparturesTab)
        asyncio.create_task(departures_tab.refresh_departures())

    def action_focus_departures(self) -> None:
        """Focus on the departures tab."""
        self.query_one("#departures-tab").focus()


def main() -> None:
    """Run the TUI application."""
    app = SofiaTrafficApp()
    app.run()


if __name__ == "__main__":
    main()
