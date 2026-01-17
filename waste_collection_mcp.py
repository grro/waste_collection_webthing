from waste_collection import WasteCollectionSchedule
from mcplib.server import MCPServer

class WasteCollectionScheduleMCPServer(MCPServer):
    """
    MCP Server that provides information about waste collection dates
    (Recycling, Bio, Residual, and Paper waste).
    """

    def __init__(self, name: str, port: int, schedule: WasteCollectionSchedule):
        super().__init__(name, port)
        self.schedule = schedule

        @self.mcp.tool(name="get_waste_schedule", description="Returns the next collection dates for all waste types.")
        def get_waste_schedule() -> str:
            """
            Fetches the next scheduled dates for waste pickup.
            Use this to answer questions about when the trash will be collected.
            """
            try:
                # Using a multiline string for better readability by the AI
                return (
                    f"Next Waste Collection Dates:\n"
                    f"- Recycling (Gelber Sack): {self.schedule.next_recycling}\n"
                    f"- Bio Waste: {self.schedule.next_organic}\n"
                    f"- Residual Waste (Restmüll): {self.schedule.next_residual}\n"
                    f"- Paper Waste: {self.schedule.next_paper}"
                )
            except Exception as e:
                return f"Error retrieving waste schedule: {str(e)}"

# npx @modelcontextprotocol/inspector <path_to_script>