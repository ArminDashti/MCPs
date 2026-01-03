planner /
├── pyproject.toml       # Dependencies (mcp, pydantic, etc.)
├── README.md            # Usage instructions & MCP config snippet
├── .env                 # Secrets (API keys, DB credentials)
├── src/
│   ├── __init__.py
│   ├── instruction.md   # Instruction for the planner
│   ├── server.py        # Main entry point
│   ├── config.py        # Environment settings & constants
│   ├── tools/           # Folder for "Tools" (executable functions)
│   │   ├── __init__.py
│   │   ├── planner.py
│   └── utils/         
│       ├── __init__.py
│       └── logger.py
└── tests/
    ├── __init__.py
    └── run_for_test.py