"""Tests for SaveImageWithSeed empty-input guard behavior."""

from __future__ import annotations

import importlib
import sys
import types
from unittest.mock import Mock


def _load_utility_nodes_with_stubs():
    """Import utility_nodes with lightweight stubs for ComfyUI modules."""
    comfy_module = types.ModuleType("comfy")
    comfy_sample_module = types.ModuleType("comfy.sample")
    setattr(comfy_sample_module, "prepare_noise", lambda *args, **kwargs: None)
    setattr(comfy_module, "sample", comfy_sample_module)

    comfy_cli_args_module = types.ModuleType("comfy.cli_args")
    setattr(comfy_cli_args_module, "args", types.SimpleNamespace(disable_metadata=False))

    folder_paths_module = types.ModuleType("folder_paths")
    setattr(folder_paths_module, "get_output_directory", Mock(return_value="output"))
    setattr(
        folder_paths_module,
        "get_save_image_path",
        Mock(side_effect=AssertionError("get_save_image_path should not be called for empty inputs")),
    )

    sys.modules["comfy"] = comfy_module
    sys.modules["comfy.sample"] = comfy_sample_module
    sys.modules["comfy.cli_args"] = comfy_cli_args_module
    sys.modules["folder_paths"] = folder_paths_module

    sys.modules.pop("utility_nodes", None)
    utility_nodes = importlib.import_module("utility_nodes")
    return utility_nodes, folder_paths_module


class _ZeroBatchTensorLike:
    """Tensor-like object with shape[0] == 0 and no length protocol."""

    shape = (0, 64, 64, 3)

    def __len__(self):
        raise TypeError("len not supported")


def test_save_images_impl_with_none_returns_empty_and_skips_io():
    utility_nodes, folder_paths_module = _load_utility_nodes_with_stubs()
    node = utility_nodes.SaveImageWithSeed()

    listdir_mock = Mock(side_effect=AssertionError("os.listdir should not be called for empty inputs"))
    utility_nodes.os.listdir = listdir_mock

    result = node._save_images_impl(None, "ComfyUI")

    assert result == {"ui": {"images": []}}
    folder_paths_module.get_save_image_path.assert_not_called()
    listdir_mock.assert_not_called()


def test_save_images_impl_with_empty_list_returns_empty_and_skips_io():
    utility_nodes, folder_paths_module = _load_utility_nodes_with_stubs()
    node = utility_nodes.SaveImageWithSeed()

    listdir_mock = Mock(side_effect=AssertionError("os.listdir should not be called for empty inputs"))
    utility_nodes.os.listdir = listdir_mock

    result = node._save_images_impl([], "ComfyUI")

    assert result == {"ui": {"images": []}}
    folder_paths_module.get_save_image_path.assert_not_called()
    listdir_mock.assert_not_called()


def test_save_images_impl_with_zero_batch_tensor_like_returns_empty_and_skips_io():
    utility_nodes, folder_paths_module = _load_utility_nodes_with_stubs()
    node = utility_nodes.SaveImageWithSeed()

    listdir_mock = Mock(side_effect=AssertionError("os.listdir should not be called for empty inputs"))
    utility_nodes.os.listdir = listdir_mock

    result = node._save_images_impl(_ZeroBatchTensorLike(), "ComfyUI")

    assert result == {"ui": {"images": []}}
    folder_paths_module.get_save_image_path.assert_not_called()
    listdir_mock.assert_not_called()
