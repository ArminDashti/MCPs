"""
MCP Planner - An AI-powered planning tool for MCP servers.

This package provides comprehensive planning capabilities through MCP protocol,
allowing AI assistants to generate structured, actionable plans for complex tasks.
"""

__version__ = "0.1.0"
__author__ = "Armin Dashti"

from .config import Config
from .tools import planner

__all__ = ["Config", "planner"]