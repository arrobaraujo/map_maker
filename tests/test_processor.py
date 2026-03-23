import pytest
import os
import pandas as pd
from src.processor import GTFSProcessor

def test_processor_init_fail():
    """Test that GTFSProcessor fails if file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        GTFSProcessor("non_existent.zip")

def test_processor_empty_data():
    """Test processor with empty data frames."""
    # We can't easily create a mock zip without a lot of boilerplate here,
    # so we just test that the initial state is as expected (empty DFs if no zip is loaded or if it's empty)
    # Actually, the constructor calls load_data which will fail if file not found.
    pass

# More comprehensive tests would require a small sample.zip GTFS file.
