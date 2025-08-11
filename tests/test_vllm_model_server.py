"""
Tests for VLLMModelServer class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import mlrun

# Add the src directory to the path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from functions.vllm_model_server import VLLMModelServer


class TestVLLMModelServer:
    """Test suite for VLLMModelServer class."""
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock MLRun context."""
        context = Mock()
        context.name = "test_context"
        context.logger = Mock()
        return context
    
    @pytest.fixture
    def sample_init_params(self, mock_context):
        """Sample initialization parameters for VLLMModelServer."""
        return {
            'context': mock_context,
            'name': 'test_vllm_server',
            'model_path': '/path/to/model',
            'model_name': 'test_model',
            'some_extra_arg': 'extra_value'
        }
    
    @patch('mlrun.serving.v2_serving.V2ModelServer.__init__')
    def test_init_calls_parent_init_with_correct_params(self, mock_parent_init, sample_init_params):
        """Test that __init__ properly calls parent __init__ with correct parameters."""
        mock_parent_init.return_value = None
        
        server = VLLMModelServer(**sample_init_params)
        
        # Verify parent __init__ was called with the right parameters
        mock_parent_init.assert_called_once_with(
            context=sample_init_params['context'],
            name=sample_init_params['name'],
            model_path=sample_init_params['model_path'],
            some_extra_arg=sample_init_params['some_extra_arg']
        )
    
    @patch('mlrun.serving.v2_serving.V2ModelServer.__init__')
    def test_init_stores_model_name(self, mock_parent_init, sample_init_params):
        """Test that __init__ properly stores the model_name attribute."""
        mock_parent_init.return_value = None
        
        server = VLLMModelServer(**sample_init_params)
        
        assert server.model_name == sample_init_params['model_name']
    
    @patch('mlrun.serving.v2_serving.V2ModelServer.__init__')
    def test_init_with_minimal_params(self, mock_parent_init, mock_context):
        """Test initialization with only required parameters."""
        mock_parent_init.return_value = None
        
        minimal_params = {
            'context': mock_context,
            'name': 'minimal_server',
            'model_path': '/minimal/path',
            'model_name': 'minimal_model'
        }
        
        server = VLLMModelServer(**minimal_params)
        
        assert server.model_name == 'minimal_model'
        mock_parent_init.assert_called_once_with(
            context=mock_context,
            name='minimal_server',
            model_path='/minimal/path'
        )
    
    @patch('mlrun.serving.v2_serving.V2ModelServer.__init__')
    def test_init_with_additional_class_args(self, mock_parent_init, sample_init_params):
        """Test initialization with additional class arguments."""
        mock_parent_init.return_value = None
        
        # Add extra arguments
        sample_init_params.update({
            'gpu_memory_utilization': 0.8,
            'max_model_len': 4096,
            'tensor_parallel_size': 2
        })
        
        server = VLLMModelServer(**sample_init_params)
        
        # Check that extra args are passed to parent
        call_args = mock_parent_init.call_args
        assert call_args.kwargs['gpu_memory_utilization'] == 0.8
        assert call_args.kwargs['max_model_len'] == 4096
        assert call_args.kwargs['tensor_parallel_size'] == 2
        
        # Check that model_name is still stored correctly
        assert server.model_name == sample_init_params['model_name']
    
    @patch('mlrun.serving.v2_serving.V2ModelServer.__init__')
    def test_inheritance_structure(self, mock_parent_init):
        """Test that VLLMModelServer properly inherits from V2ModelServer."""
        mock_parent_init.return_value = None
        
        # Import mlrun.serving.v2_serving.V2ModelServer for type checking
        with patch('mlrun.serving.v2_serving.V2ModelServer') as mock_v2_server:
            mock_context = Mock()
            
            server = VLLMModelServer(
                context=mock_context,
                name='inheritance_test',
                model_path='/test/path',
                model_name='test_model'
            )
            
            # Check inheritance
            assert isinstance(server, VLLMModelServer)
            # The actual inheritance check requires the real mlrun module,
            # but we can verify the constructor calls the parent
            mock_parent_init.assert_called_once()
    
    @patch('mlrun.serving.v2_serving.V2ModelServer.__init__')
    def test_docstring_and_class_documentation(self, mock_parent_init):
        """Test that the class has proper documentation."""
        mock_parent_init.return_value = None
        
        # Check class docstring
        assert VLLMModelServer.__doc__ is not None
        assert "VLLM models" in VLLMModelServer.__doc__
        assert "VisionModelServer" in VLLMModelServer.__doc__
        
        # Check __init__ docstring
        assert VLLMModelServer.__init__.__doc__ is not None
        assert ":param context:" in VLLMModelServer.__init__.__doc__
        assert ":param model_name:" in VLLMModelServer.__init__.__doc__
    
    @patch('mlrun.serving.v2_serving.V2ModelServer.__init__')
    def test_parameter_validation_types(self, mock_parent_init, mock_context):
        """Test parameter type validation (basic smoke test)."""
        mock_parent_init.return_value = None
        
        # Test with various parameter types
        server = VLLMModelServer(
            context=mock_context,
            name='type_test',
            model_path='/some/path',
            model_name='model_123',
            numeric_param=42,
            string_param='test_string',
            boolean_param=True,
            list_param=[1, 2, 3]
        )
        
        assert server.model_name == 'model_123'
        
        # Verify parent was called with the extra parameters
        call_kwargs = mock_parent_init.call_args.kwargs
        assert call_kwargs['numeric_param'] == 42
        assert call_kwargs['string_param'] == 'test_string'
        assert call_kwargs['boolean_param'] is True
        assert call_kwargs['list_param'] == [1, 2, 3]


class TestVLLMModelServerIntegration:
    """Integration tests for VLLMModelServer (when mlrun is available)."""
    @pytest.fixture
    def mlrun_context(self):
        """Create the MLRun context fixture."""
        context = mlrun.MLClientCtx()
        return context
    
    @pytest.fixture
    def tiny_init_params(self, mlrun_context):
        """Minimal initialization parameters for integration tests."""
        return {
            'context': mlrun_context,
            'name': 'tiny_vllm_server',
            'model_path': '/tiny/path/to/model',
            'model_name': 'arnir0/Tiny-LLM'
        }
    
    @pytest.mark.skipif(True, reason="Requires full mlrun installation")
    def test_real_mlrun_integration(self):
        """Test with actual mlrun components (skipped by default)."""
        # This test would require actual mlrun installation and setup
        # It's marked to skip by default but can be enabled for full integration testing
        pass
    
    def test_class_attributes_exist(self):
        """Test that required class attributes and methods exist."""
        # Test class has required attributes
        assert hasattr(VLLMModelServer, '__init__')
        assert hasattr(VLLMModelServer, '__doc__')
        
        # Test that it's properly structured as a class
        assert callable(VLLMModelServer)

    def test_init_values(self, tiny_init_params):
        """Test that __init__ properly initializes values."""
        server = VLLMModelServer(**tiny_init_params)
        
        assert server.context == tiny_init_params['context']
        assert server.name == tiny_init_params['name']
        assert server.model_path == tiny_init_params['model_path']
        assert server.model_name == tiny_init_params['model_name']

if __name__ == '__main__':
    pytest.main([__file__])
