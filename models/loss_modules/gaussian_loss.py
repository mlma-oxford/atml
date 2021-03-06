from .base_loss import _BaseLoss

from typing import Dict, Tuple

import torch.nn.functional as F
import torch

class GaussianLoss(_BaseLoss):

    def __init__(self):
        _BaseLoss.__init__(self)

    def compute_loss(self, x, vae_output, warm_up=1) -> Tuple[torch.Tensor, Dict, torch.Tensor]:
        """
        Computes the loss between the network input and output assuming the
        approximate posterior is a fully-factorized Gaussian.
        
        :param x: input to the VAE
        :param vae_output: output of the VAE
        :param warm_up: the entropy annealing factor (warm-up).
        :return (loss, loss_metrics, log_p_x): information about the loss
        """
        vae_reconstruction = vae_output['x_hat']
        vae_latent = vae_output['z']
        mean, log_var = vae_output['params']

        # Calculate the logs in the ELBO with ONE sample from the expectation.
        #   ELBO = E[log(p(x,z) / q(z|x))]
        #        = E[log(p(x|z) * p(z) / q(z|x))]
        #        = E[log p(x|z) + log p(z) - log q(z|x)]
        log_p_xz = -F.binary_cross_entropy_with_logits(vae_reconstruction, x, reduction='none').view(x.shape[0], -1).sum(1)
        log_p_z = -0.5 * vae_latent.pow(2).sum(1)
        log_q_zx = -0.5 * (log_var.sum(1) + ((vae_latent - mean).pow(2) / torch.exp(log_var)).sum(1))

        log_p_x = log_p_xz + log_p_z - warm_up * log_q_zx

        # The ELBO is defined to be the mean of the logs in the batch.
        elbo = torch.mean(log_p_x)

        # Maximizing the ELBO is equivalent to minimizing the negative ELBO.
        loss = -elbo

        loss_metrics = {}
        loss_metrics["elbo"] = float(elbo)
        loss_metrics["log p(x|z)"] = float(torch.mean(log_p_xz))
        loss_metrics["log p(z)"] = float(torch.mean(log_p_z))
        loss_metrics["log q(z|x)"] = float(torch.mean(log_q_zx))

        return loss, loss_metrics, log_p_x
