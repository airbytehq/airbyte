# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

import pytest

from PyInstaller.utils.tests import importorskip


# Run the tests in onedir mode only
torch_onedir_only = pytest.mark.parametrize('pyi_builder', ['onedir'], indirect=True)


@importorskip('torch')
@torch_onedir_only
def test_torch(pyi_builder):
    pyi_builder.test_source("""
        import torch

        torch.rand((10, 10)) * torch.rand((10, 10))
    """)


# Test with torchaudio transform that uses torchcript, which requires
# access to transforms' sources.
@importorskip('torchaudio')
@torch_onedir_only
def test_torchaudio_scripted_transforms(pyi_builder):
    pyi_builder.test_source("""
        import numpy as np

        import torch.nn
        import torchaudio.transforms

        # Generate a sine waveform
        volume = 0.5  # range [0.0, 1.0]
        sampling_rate = 44100  # sampling rate, Hz
        duration = 5.0  # seconds
        freq = 500.0  # sine frequency, Hz

        points = np.arange(0, sampling_rate * duration)
        signal = volume * np.sin(2 * np.pi * points * freq / sampling_rate)

        # Resample the signal using scripted transform
        transforms = torch.nn.Sequential(
            torchaudio.transforms.Resample(
                orig_freq=sampling_rate,
                new_freq=sampling_rate // 2
            ),
        )
        scripted_transforms = torch.jit.script(transforms)

        signal_tensor = torch.from_numpy(signal).float()
        resampled_tensor = scripted_transforms(signal_tensor)

        print("Result size:", resampled_tensor.size())
        assert len(resampled_tensor) == len(signal_tensor) / 2
    """)


# Test with torchtext transform that uses torchcript, which requires
# access to transforms' sources.
@importorskip('torchtext')
@torch_onedir_only
def test_torchtext_scripted_berta_tokenizer_transform(pyi_builder):
    pyi_builder.test_source("""
        import torch.nn
        import torchtext.models
        import torchtext.functional

        # Create Roberta Encoder with Base configuration
        roberta_base = torchtext.models.ROBERTA_BASE_ENCODER
        classifier_head = torchtext.models.RobertaClassificationHead(num_classes=2, input_dim=768)
        transform = roberta_base.transform()

        # Create transform that uses torchscript
        scripted_transform = torch.jit.script(transform)
        print(scripted_transform)

        # Prepare test data
        small_input_batch = [
            "Hello world",
            "How are you!",
        ]

        model_input = torchtext.functional.to_tensor(scripted_transform(small_input_batch), padding_value=1)
        print("Tokenized input:", model_input)

        # Process
        if False:
            # Downloads the model (~ 240 MB), if necessary.
            model = roberta_base.get_model(head=classifier_head)

            output = model(model_input)
            print(output)
            print(output.shape)
    """)


@importorskip('torchvision')
@torch_onedir_only
def test_torchvision_nms(pyi_builder):
    pyi_builder.test_source("""
        import torch
        import torchvision
        # boxes: Nx4 tensor (x1, y1, x2, y2)
        boxes = torch.tensor([
            [0.0, 0.0, 1.0, 1.0],
            [0.45, 0.0, 1.0, 1.0],
        ])
        # scores: Nx1 tensor
        scores = torch.tensor([
            1.0,
            1.1
        ])
        keep = torchvision.ops.nms(boxes, scores, 0.5)
        # The boxes have IoU of 0.55, and the second one has a slightly
        # higher score, so we expect it to be kept while the first one
        # is discarded.
        assert keep == 1
    """)


# Ensure that torchvision.io.image manages to load torchvision.image extension for its ops.
@importorskip('torchvision')
@torch_onedir_only
def test_torchvision_image_io(pyi_builder):
    pyi_builder.test_source("""
        import torch
        import torchvision.io.image

        image = torch.zeros((3, 100, 100), dtype=torch.uint8)
        png_data = torchvision.io.image.encode_png(image)
        decoded_image = torchvision.io.image.decode_png(png_data)

        assert torch.equal(image, decoded_image), "Original and decoded image are not identical!"
    """)


# Advanced tests that uses torchvision.datasets and torchvision.transforms;
# the transforms are combined using torchscript, which requires access to
# transforms' sources.
@importorskip('torchvision')
@torch_onedir_only
def test_torchvision_scripted_transforms(pyi_builder):
    pyi_builder.test_source("""
        import torch
        import torch.nn

        import torchvision.transforms
        import torchvision.datasets

        # Generate one image, and convert it from PIL to tensor
        preproc = torchvision.transforms.Compose([
            torchvision.transforms.PILToTensor()
        ])

        dataset = torchvision.datasets.FakeData(
            size=1,  # 1 image
            image_size=(3, 200, 200),
            num_classes=2,
            transform=preproc,
        )

        assert len(dataset) == 1
        image, category = dataset[0]

        assert image.size() == (3, 200, 200)
        assert image.dtype == torch.uint8

        # Create a composite transform that uses torchscript
        transforms = torch.nn.Sequential(
            torchvision.transforms.RandomCrop(100),
            torchvision.transforms.RandomHorizontalFlip(p=0.3),
        )
        scripted_transforms = torch.jit.script(transforms)

        # Transform image
        transformed_image = scripted_transforms(image)

        assert transformed_image.size() == (3, 100, 100)
        assert transformed_image.dtype == torch.uint8
    """)
