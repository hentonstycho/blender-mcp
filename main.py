from blender_mcp.server import main as server_main

# Personal fork - added startup message for easier debugging
def main():
    """Entry point for the blender-mcp package"""
    print("Starting Blender MCP server...")
    server_main()

if __name__ == "__main__":
    main()
