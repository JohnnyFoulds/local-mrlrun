"""
Pytest configuration and shared fixtures for the test suite.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


@pytest.fixture
def mock_mlrun_context():
    """Create a mock MLRun context that can be reused across tests."""
    context = Mock()
    context.name = "test_context"
    context.logger = Mock()
    context.logger.info = Mock()
    context.logger.warning = Mock()
    context.logger.error = Mock()
    context.logger.debug = Mock()
    return context


@pytest.fixture
def mock_mlrun_modules():
    """Mock mlrun modules to avoid import errors during testing."""
    # Create mock modules
    mock_mlrun = Mock()
    mock_serving = Mock()
    mock_v2_serving = Mock()
    
    # Create a mock V2ModelServer class
    mock_v2_server = Mock()
    mock_v2_server.__init__ = Mock(return_value=None)
    
    # Set up the module structure
    mock_v2_serving.V2ModelServer = mock_v2_server
    mock_serving.v2_serving = mock_v2_serving
    mock_mlrun.serving = mock_serving
    mock_mlrun.MLClientCtx = Mock
    
    with patch.dict('sys.modules', {
        'mlrun': mock_mlrun,
        'mlrun.serving': mock_serving,
        'mlrun.serving.v2_serving': mock_v2_serving,
    }):
        yield mock_v2_server
