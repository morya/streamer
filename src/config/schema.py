"""
Configuration schema validation for the screen streaming application.
"""

from typing import Dict, Any, List, Union
import re


class ConfigValidator:
    """Validates configuration against schema."""
    
    # Schema definition
    SCHEMA = {
        "type": "object",
        "properties": {
            "capture": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "enum": ["1/4", "1/2", "full"]
                    },
                    "fps": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 240
                    }
                },
                "required": ["region", "fps"]
            },
            "encoding": {
                "type": "object",
                "properties": {
                    "bitrate": {
                        "type": "string",
                        "pattern": r"^\d+Mbps$|^Custom$"
                    },
                    "protocol": {
                        "type": "string",
                        "enum": ["rtmp", "srt"]
                    },
                    "preset": {
                        "type": "string",
                        "enum": ["ultrafast", "superfast", "veryfast", "faster", 
                                "fast", "medium", "slow", "slower", "veryslow"]
                    }
                },
                "required": ["bitrate", "protocol", "preset"]
            },
            "streaming": {
                "type": "object",
                "properties": {
                    "last_url": {
                        "type": "string"
                    },
                    "auto_start": {
                        "type": "boolean"
                    }
                },
                "required": ["last_url", "auto_start"]
            },
            "ui": {
                "type": "object",
                "properties": {
                    "window_position": {
                        "type": "array",
                        "items": {
                            "type": "integer",
                            "minimum": 0
                        },
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "always_on_top": {
                        "type": "boolean"
                    },
                    "theme": {
                        "type": "string",
                        "enum": ["dark", "light", "system"]
                    }
                },
                "required": ["window_position", "always_on_top", "theme"]
            }
        },
        "required": ["capture", "encoding", "streaming", "ui"]
    }
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> List[str]:
        """Validate configuration against schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of validation error messages, empty if valid
        """
        errors = []
        
        # Check root level
        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return errors
            
        # Check required sections
        for section in cls.SCHEMA["required"]:
            if section not in config:
                errors.append(f"Missing required section: {section}")
                
        # Validate each section
        for section, section_config in config.items():
            if section in cls.SCHEMA["properties"]:
                section_errors = cls._validate_section(
                    section, section_config, cls.SCHEMA["properties"][section]
                )
                errors.extend(section_errors)
                
        return errors
        
    @classmethod
    def _validate_section(cls, section_name: str, section_data: Any, 
                         section_schema: Dict[str, Any]) -> List[str]:
        """Validate a configuration section.
        
        Args:
            section_name: Name of the section
            section_data: Section data to validate
            section_schema: Schema for the section
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check section type
        if section_schema.get("type") == "object":
            if not isinstance(section_data, dict):
                errors.append(f"Section '{section_name}' must be a dictionary")
                return errors
                
            # Check required properties
            for prop in section_schema.get("required", []):
                if prop not in section_data:
                    errors.append(f"Missing required property: {section_name}.{prop}")
                    
            # Validate each property
            for prop, prop_value in section_data.items():
                if prop in section_schema.get("properties", {}):
                    prop_errors = cls._validate_property(
                        f"{section_name}.{prop}", prop_value, 
                        section_schema["properties"][prop]
                    )
                    errors.extend(prop_errors)
                    
        return errors
        
    @classmethod
    def _validate_property(cls, prop_path: str, prop_value: Any, 
                          prop_schema: Dict[str, Any]) -> List[str]:
        """Validate a configuration property.
        
        Args:
            prop_path: Path to the property (e.g., "capture.region")
            prop_value: Property value to validate
            prop_schema: Schema for the property
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check type
        expected_type = prop_schema.get("type")
        if expected_type:
            type_valid = cls._check_type(prop_value, expected_type)
            if not type_valid:
                errors.append(
                    f"Property '{prop_path}' must be of type {expected_type}, "
                    f"got {type(prop_value).__name__}"
                )
                return errors  # Stop further validation if type is wrong
                
        # Check enum
        if "enum" in prop_schema:
            if prop_value not in prop_schema["enum"]:
                errors.append(
                    f"Property '{prop_path}' must be one of {prop_schema['enum']}, "
                    f"got '{prop_value}'"
                )
                
        # Check pattern
        if "pattern" in prop_schema:
            pattern = prop_schema["pattern"]
            if not re.match(pattern, str(prop_value)):
                errors.append(
                    f"Property '{prop_path}' must match pattern {pattern}, "
                    f"got '{prop_value}'"
                )
                
        # Check minimum/maximum for numbers
        if isinstance(prop_value, (int, float)):
            if "minimum" in prop_schema and prop_value < prop_schema["minimum"]:
                errors.append(
                    f"Property '{prop_path}' must be >= {prop_schema['minimum']}, "
                    f"got {prop_value}"
                )
            if "maximum" in prop_schema and prop_value > prop_schema["maximum"]:
                errors.append(
                    f"Property '{prop_path}' must be <= {prop_schema['maximum']}, "
                    f"got {prop_value}"
                )
                
        # Check array properties
        if expected_type == "array":
            if not isinstance(prop_value, list):
                errors.append(f"Property '{prop_path}' must be a list")
                return errors
                
            # Check min/max items
            if "minItems" in prop_schema and len(prop_value) < prop_schema["minItems"]:
                errors.append(
                    f"Property '{prop_path}' must have at least {prop_schema['minItems']} items, "
                    f"got {len(prop_value)}"
                )
            if "maxItems" in prop_schema and len(prop_value) > prop_schema["maxItems"]:
                errors.append(
                    f"Property '{prop_path}' must have at most {prop_schema['maxItems']} items, "
                    f"got {len(prop_value)}"
                )
                
            # Validate array items
            if "items" in prop_schema:
                for i, item in enumerate(prop_value):
                    item_errors = cls._validate_property(
                        f"{prop_path}[{i}]", item, prop_schema["items"]
                    )
                    errors.extend(item_errors)
                    
        return errors
        
    @classmethod
    def _check_type(cls, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type.
        
        Args:
            value: Value to check
            expected_type: Expected type name
            
        Returns:
            True if type matches, False otherwise
        """
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if expected_type in type_map:
            expected = type_map[expected_type]
            if isinstance(expected, tuple):
                return isinstance(value, expected)
            return isinstance(value, expected)
            
        return False
        
    @classmethod
    def sanitize(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize configuration by removing invalid fields and fixing values.
        
        Args:
            config: Configuration dictionary to sanitize
            
        Returns:
            Sanitized configuration dictionary
        """
        sanitized = {}
        
        # Only include sections defined in schema
        for section, section_schema in cls.SCHEMA["properties"].items():
            if section in config:
                section_data = config[section]
                if section_schema.get("type") == "object" and isinstance(section_data, dict):
                    sanitized[section] = cls._sanitize_section(section_data, section_schema)
                    
        return sanitized
        
    @classmethod
    def _sanitize_section(cls, section_data: Dict[str, Any], 
                         section_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a configuration section.
        
        Args:
            section_data: Section data to sanitize
            section_schema: Schema for the section
            
        Returns:
            Sanitized section data
        """
        sanitized = {}
        
        for prop, prop_schema in section_schema.get("properties", {}).items():
            if prop in section_data:
                prop_value = section_data[prop]
                
                # Type conversion
                expected_type = prop_schema.get("type")
                if expected_type:
                    prop_value = cls._convert_type(prop_value, expected_type)
                    
                # Enum validation
                if "enum" in prop_schema and prop_value not in prop_schema["enum"]:
                    # Use first enum value as default
                    prop_value = prop_schema["enum"][0]
                    
                # Pattern validation for strings
                if (expected_type == "string" and "pattern" in prop_schema and 
                    not re.match(prop_schema["pattern"], str(prop_value))):
                    # Use a safe default
                    if prop_schema["pattern"] == r"^\d+Mbps$|^Custom$":
                        prop_value = "2Mbps"
                        
                # Range validation for numbers
                if isinstance(prop_value, (int, float)):
                    if "minimum" in prop_schema and prop_value < prop_schema["minimum"]:
                        prop_value = prop_schema["minimum"]
                    if "maximum" in prop_schema and prop_value > prop_schema["maximum"]:
                        prop_value = prop_schema["maximum"]
                        
                sanitized[prop] = prop_value
                
        return sanitized
        
    @classmethod
    def _convert_type(cls, value: Any, expected_type: str) -> Any:
        """Convert value to expected type if possible.
        
        Args:
            value: Value to convert
            expected_type: Expected type name
            
        Returns:
            Converted value
        """
        try:
            if expected_type == "string":
                return str(value)
            elif expected_type == "integer":
                return int(value)
            elif expected_type == "number":
                return float(value)
            elif expected_type == "boolean":
                if isinstance(value, str):
                    return value.lower() in ("true", "yes", "1", "on")
                return bool(value)
            elif expected_type == "array":
                if isinstance(value, list):
                    return value
                return [value]
            elif expected_type == "object":
                if isinstance(value, dict):
                    return value
                return {}
        except (ValueError, TypeError):
            # Return default based on type
            defaults = {
                "string": "",
                "integer": 0,
                "number": 0.0,
                "boolean": False,
                "array": [],
                "object": {}
            }
            return defaults.get(expected_type, value)
            
        return value