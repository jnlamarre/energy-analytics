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


class TestFilesEnhanced:
    """Enhanced file operation tests with comprehensive validation."""

    def test_file_content_validation_comprehensive(self):
        """Test comprehensive file content validation with various data types."""
        test_data = [
            {"id": 1, "name": "Alice", "score": 95.5, "active": True},
            {"id": 2, "name": "Bob", "score": 87.2, "active": False},
            {"id": 3, "name": "Charlie", "score": 92.8, "active": True}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save and verify file properties
            save_json(test_data, temp_path)
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
            
            # Verify raw content contains expected elements
            with open(temp_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                assert '"id": 1' in raw_content
                assert '"name": "Alice"' in raw_content
                assert '"score": 95.5' in raw_content
                assert '"active": true' in raw_content
            
            # Load and verify complete data integrity
            loaded_data = load_json(temp_path)
            assert loaded_data == test_data
            assert len(loaded_data) == 3
            
            # Verify specific field values with proper type checking
            assert loaded_data[0]["name"] == "Alice"
            assert loaded_data[1]["score"] == 87.2
            assert loaded_data[2]["active"] is True
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_unicode_encoding_handling(self):
        """Test proper Unicode character encoding and preservation."""
        unicode_data = [
            {"name": "café", "city": "São Paulo", "description": "été"},
            {"symbols": "🚀 📊 ⚡", "mixed": "ASCII + français + 🌟"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save and load Unicode data
            save_json(unicode_data, temp_path)
            
            # Verify file can be read with UTF-8 encoding
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "café" in content
                assert "São Paulo" in content
                assert "été" in content
                assert "🚀" in content
            
            # Verify data integrity through load operation
            loaded_data = load_json(temp_path)
            assert loaded_data == unicode_data
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)