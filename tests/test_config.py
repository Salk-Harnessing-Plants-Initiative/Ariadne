"""Tests for the config module."""

import pytest
from ariadne_roots import config


class TestConfigDefaults:
    """Test default configuration values."""

    def test_default_scale_factor(self):
        """Test that default scale factor is 1.0."""
        # Reset to defaults (in case other tests modified)
        config.length_scale_factor = 1.0
        config.length_scale_unit = "px"

        assert config.length_scale_factor == 1.0

    def test_default_scale_unit(self):
        """Test that default scale unit is 'px'."""
        # Reset to defaults
        config.length_scale_factor = 1.0
        config.length_scale_unit = "px"

        assert config.length_scale_unit == "px"


class TestConfigSetters:
    """Test setting custom configuration values."""

    def test_set_custom_scale_factor(self):
        """Test setting a custom scale factor."""
        config.length_scale_factor = 2.5
        assert config.length_scale_factor == 2.5

        # Reset to default
        config.length_scale_factor = 1.0

    def test_set_custom_unit(self):
        """Test setting a custom unit."""
        config.length_scale_unit = "mm"
        assert config.length_scale_unit == "mm"

        # Reset to default
        config.length_scale_unit = "px"

    def test_scale_factor_persistence(self):
        """Test that scale factor persists across reads."""
        config.length_scale_factor = 3.14159

        # Multiple reads should return the same value
        first_read = config.length_scale_factor
        second_read = config.length_scale_factor
        third_read = config.length_scale_factor

        assert first_read == 3.14159
        assert second_read == 3.14159
        assert third_read == 3.14159

        # Reset to default
        config.length_scale_factor = 1.0

    def test_scale_unit_persistence(self):
        """Test that scale unit persists across reads."""
        config.length_scale_unit = "cm"

        # Multiple reads should return the same value
        first_read = config.length_scale_unit
        second_read = config.length_scale_unit
        third_read = config.length_scale_unit

        assert first_read == "cm"
        assert second_read == "cm"
        assert third_read == "cm"

        # Reset to default
        config.length_scale_unit = "px"
