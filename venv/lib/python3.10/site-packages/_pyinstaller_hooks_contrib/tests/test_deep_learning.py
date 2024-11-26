# ------------------------------------------------------------------
# Copyright (c) 2023 PyInstaller Development Team.
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
onedir_only = pytest.mark.parametrize('pyi_builder', ['onedir'], indirect=True)


# Basic transformers test with BERT-based unmasker
@importorskip('transformers')
@importorskip('torch')
@onedir_only
def test_transformers_bert_pipeline(pyi_builder):
    pyi_builder.test_source("""
        import transformers
        unmasker = transformers.pipeline('fill-mask', model='bert-base-uncased')
        output = unmasker("Hello I'm a [MASK] model.")
        print("Unmasked text:", output)
    """)


# Trying to import DebertaModel triggers error about missing source files for TorchScript
@importorskip('transformers')
@importorskip('torch')
@onedir_only
def test_transformers_deberta_import(pyi_builder):
    pyi_builder.test_source("""
        from transformers import DebertaConfig, DebertaModel

        configuration = DebertaConfig()
        model = DebertaModel(configuration)
    """)


# Building models from tabular data example from https://docs.fast.ai/quick_start.html
@importorskip('fastai')
@onedir_only
def test_fastai_tabular_data(pyi_builder):
    pyi_builder.test_source("""
        from fastai.tabular.all import *

        path = untar_data(URLs.ADULT_SAMPLE)
        print(f"Dataset path: {path}")

        dls = TabularDataLoaders.from_csv(
            path/'adult.csv',
            path=path,
            y_names="salary",
            cat_names = [
                'workclass',
                'education',
                'marital-status',
                'occupation',
                'relationship',
                'race',
            ],
            cont_names = [
                'age',
                'fnlwgt',
                'education-num',
            ],
            procs = [
                Categorify,
                FillMissing,
                Normalize,
            ],
        )

        learn = tabular_learner(dls, metrics=accuracy)
        learn.fit_one_cycle(2)
        learn.show_results()
    """)


@importorskip('timm')
@onedir_only
def test_timm_model_creation(pyi_builder):
    pyi_builder.test_source("""
        import timm

        # List available models
        pretrained_models = timm.list_models(pretrained=True)
        print(f"Pre-trained models: {len(pretrained_models)}")
        assert len(pretrained_models) > 0

        # Create a model (non-trained version, to avoid downloading weights)
        model = timm.create_model("resnet50d", pretrained=False)
        print(model)
    """)


@importorskip('lightning')
@importorskip('torchvision')
@importorskip('torch')
@onedir_only
def test_lightning_mnist_autoencoder(pyi_builder):
    pyi_builder.test_source("""
        import os

        # On macOS, multiprocessing seems to be used at some point...
        if __name__ == '__main__':
            import multiprocessing
            multiprocessing.freeze_support()

        import torch
        import torchvision
        import lightning


        class LitAutoEncoder(lightning.LightningModule):
            def __init__(self):
                super().__init__()
                self.encoder = torch.nn.Sequential(
                    torch.nn.Linear(28 * 28, 128),
                    torch.nn.ReLU(),
                    torch.nn.Linear(128, 3),
                )
                self.decoder = torch.nn.Sequential(
                    torch.nn.Linear(3, 128),
                    torch.nn.ReLU(),
                    torch.nn.Linear(128, 28 * 28),
                )

            def forward(self, x):
                embedding = self.encoder(x)
                return embedding

            def training_step(self, batch, batch_idx):
                x, y = batch
                x = x.view(x.size(0), -1)
                z = self.encoder(x)
                x_hat = self.decoder(z)
                loss = torch.nn.functional.mse_loss(x_hat, x)
                return loss

            def configure_optimizers(self):
                optimizer = torch.optim.Adam(
                    self.parameters(),
                    lr=1e-3,
                )
                return optimizer


        # Dataset
        dataset = torchvision.datasets.MNIST(
            os.path.dirname(__file__),
            download=True,
            transform=torchvision.transforms.ToTensor(),
        )
        dataset_size = len(dataset)
        num_samples = 100
        train, val = torch.utils.data.random_split(
            dataset,
            [num_samples, dataset_size - num_samples],
        )

        # Train
        autoencoder = LitAutoEncoder()
        trainer = lightning.Trainer(max_epochs=1, logger=False)
        trainer.fit(
            autoencoder,
            torch.utils.data.DataLoader(train),
        )
    """)


@importorskip('bitsandbytes')
@onedir_only
def test_bitsandbytes(pyi_builder):
    pyi_builder.test_source("""
        import bitsandbytes

        # Instantiate a model and optimizer
        dim1 = 256
        dim2 = 256
        linear = bitsandbytes.nn.Linear8bitLt(dim1, dim2, bias=True, has_fp16_weights=False, threshold=6.0)
        adam = bitsandbytes.optim.Adam8bit(linear.parameters(), lr=0.001, betas=(0.9, 0.995))
    """)


@importorskip('linear_operator')
@onedir_only
def test_linear_operator(pyi_builder):
    pyi_builder.test_source("""
        import torch
        from linear_operator.operators import DiagLinearOperator, LowRankRootLinearOperator

        diag1 = 0.1 + torch.rand(100)
        diag2 = 0.1 + torch.rand(100)

        mat1 = DiagLinearOperator(diag1)
        mat2 = DiagLinearOperator(diag2)

        result = (mat1 + mat2).diagonal()
    """)


# Based on https://docs.gpytorch.ai/en/latest/examples/01_Exact_GPs/Simple_GP_Regression.html
@importorskip('gpytorch')
@onedir_only
def test_gpytorch_simple_gp_regression(pyi_builder):
    pyi_builder.test_source("""
        import math

        import torch
        import gpytorch

        ## Training
        # Training data is 100 points in [0,1] inclusive regularly spaced
        train_x = torch.linspace(0, 1, 100)

        # True function is sin(2*pi*x) with Gaussian noise
        train_y = torch.sin(train_x * (2 * math.pi)) + torch.randn(train_x.size()) * math.sqrt(0.04)

        # We will use the simplest form of GP model, exact inference
        class ExactGPModel(gpytorch.models.ExactGP):
            def __init__(self, train_x, train_y, likelihood):
                super().__init__(train_x, train_y, likelihood)
                self.mean_module = gpytorch.means.ConstantMean()
                self.covar_module = gpytorch.kernels.ScaleKernel(gpytorch.kernels.RBFKernel())

            def forward(self, x):
                mean_x = self.mean_module(x)
                covar_x = self.covar_module(x)
                return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

        # Initialize likelihood and model
        likelihood = gpytorch.likelihoods.GaussianLikelihood()
        model = ExactGPModel(train_x, train_y, likelihood)

        # Find optimal model hyperparameters
        training_iter = 2

        model.train()
        likelihood.train()

        # Use the adam optimizer
        optimizer = torch.optim.Adam(model.parameters(), lr=0.1)  # Includes GaussianLikelihood parameters

        # "Loss" for GPs - the marginal log likelihood
        mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)

        print("Training the model...")
        for i in range(training_iter):
            # Zero gradients from previous iteration
            optimizer.zero_grad()
            # Output from model
            output = model(train_x)
            # Calc loss and backprop gradients
            loss = -mll(output, train_y)
            loss.backward()
            print('Iter %d/%d - Loss: %.3f   lengthscale: %.3f   noise: %.3f' % (
                i + 1, training_iter, loss.item(),
                model.covar_module.base_kernel.lengthscale.item(),
                model.likelihood.noise.item()
            ))
            optimizer.step()

        ## Inference
        # Get into evaluation (predictive posterior) mode
        model.eval()
        likelihood.eval()

        # Test points are regularly spaced along [0,1]
        # Make predictions by feeding model through likelihood
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            test_x = torch.linspace(0, 1, 51)
            observed_pred = likelihood(model(test_x))

        print("Test X:", test_x.numpy())
        print("Predicted Y:", observed_pred.mean.numpy())
    """)


# Basic import test for fvcore.nn, which shows that we need to collect its source.py files for TorchScript/JIT.
@importorskip('fvcore')
@onedir_only
def test_fvcore(pyi_builder):
    pyi_builder.test_source("""
        import fvcore.nn
    """)


# Basic test for detectron2, which shows that we need to collect its source.py files for TorchScript/JIT.
@importorskip('detectron2')
@onedir_only
def test_detectron2(pyi_builder):
    pyi_builder.test_source("""
        from detectron2 import model_zoo
        from detectron2.config import get_cfg
        from detectron2.engine import DefaultTrainer

        cfg = get_cfg()
        print("Config:", cfg)

        # We cannot instantiate DefaultTrainer without specifying training datasets in config...
        #trainer = DefaultTrainer(cfg)
        #print(trainer)
    """)


# Hugging Face datasets: Download squad dataset (76 MB train, 10 MB validation)
@importorskip('datasets')
@onedir_only
def test_datasets_download_squad(pyi_builder):
    pyi_builder.test_source("""
        from datasets import load_dataset
        from huggingface_hub import list_datasets

        # Print all the available datasets
        available_datasets = [dataset.id for dataset in list_datasets()]
        print("Available datasets:", len(available_datasets))

        # Load a dataset and print the first example in the training set
        print("Loading squad dataset...")
        squad_dataset = load_dataset('squad')
        print("First sample:", squad_dataset['train'][0])
    """)


# Basic test for Hugging Face accelerate framework
@importorskip('accelerate')
@onedir_only
def test_accelerate(pyi_builder):
    pyi_builder.test_source("""
        import torch
        from accelerate import Accelerator

        accelerator = Accelerator()
        device = accelerator.device
        print("Accelerator device:", device)

        model = torch.nn.Transformer().to(device)
        optimizer = torch.optim.Adam(model.parameters())

        model, optimizer = accelerator.prepare(model, optimizer)
        print("Model:", model)
        print("Optimizer:", optimizer)
    """)
