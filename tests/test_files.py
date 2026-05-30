import json
import os
import tempfile
import pytest

from utils.files import save_json, load_json


def test_save_json_successful():
    test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_path = temp_file.name
    
    try:
        save_json(test_data, temp_path)
        
        # Verify file was created and contains expected data
        assert os.path.exists(temp_path)
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_save_json_with_unicode():
    test_data = {"french": "données", "symbols": "été", "number": 123}
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_path = temp_file.name
    
    try:
        save_json(test_data, temp_path)
        
        # Verify UTF-8 encoding preserved Unicode characters
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "données" in content
        assert "été" in content
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_load_json_successful():
    test_data = {"test": True, "values": [1, 2, 3]}
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump(test_data, temp_file, ensure_ascii=False, indent=2)
        temp_path = temp_file.name
    
    try:
        loaded_data = load_json(temp_path)
        assert loaded_data == test_data
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_load_json_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_json("nonexistent_file.json")


def test_load_json_invalid_content():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write("invalid json content {")
        temp_path = temp_file.name
    
    try:
        with pytest.raises(json.JSONDecodeError):
            load_json(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_load_json_empty_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_path = temp_file.name
    
    try:
        with pytest.raises(json.JSONDecodeError):
            load_json(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_save_load_round_trip():
    original_data = {
        "string": "test",
        "number": 42,
        "float": 3.14,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
        "nested": {"key": "value"}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_path = temp_file.name
    
    try:
        save_json(original_data, temp_path)
        loaded_data = load_json(temp_path)
        
        assert loaded_data == original_data
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)