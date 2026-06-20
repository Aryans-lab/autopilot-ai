"""Unit tests for tools."""
import pytest
from nanocorp.tools.base import success_result, error_result
from nanocorp.tools.filesystem import FileWriteTool, FileReadTool
from nanocorp.tools.code import BashTool

def test_success_result():
    result = success_result(data={"key": "value"})
    assert result.success is True

def test_error_result():
    result = error_result("Error")
    assert result.success is False

def test_file_write_read(tmp_path):
    write_tool = FileWriteTool()
    read_tool = FileReadTool()
    test_file = tmp_path / "test.txt"
    result = write_tool.execute(path=str(test_file), content="Hello!")
    assert result.success is True
    read = read_tool.execute(path=str(test_file))
    assert read.success is True

def test_bash_echo():
    tool = BashTool(timeout=10)
    result = tool.execute(command="echo 'Hello NanoCorp'")
    assert result.success is True
