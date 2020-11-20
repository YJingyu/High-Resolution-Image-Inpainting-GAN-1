from typing import Tuple

import torch
from torch import nn
from torch.nn import functional as F

from high_resolution_image_inpainting_gan.network_module import (
    Conv2dLayer,
    GatedConv2d,
    TransposeGatedConv2d,
)


class Coarse(nn.Module):
    """
    Input: masked image + mask
    Output: filled image
    """

    # def __init__(self, config):
    def __init__(self, norm, activation):
        super().__init__()
        # Initialize the padding scheme
        self.coarse1 = nn.Sequential(
            # encoder
            GatedConv2d(4, 32, 5, 2, 2, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(32, 32, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(32, 64, 3, 2, 1, activation=activation, norm=norm, single_channel_conv=True),
        )
        self.coarse2 = nn.Sequential(
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
        )
        self.coarse3 = nn.Sequential(
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
        )
        self.coarse4 = nn.Sequential(
            GatedConv2d(64, 64, 3, 1, 2, dilation=2, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 2, dilation=2, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 2, dilation=2, activation=activation, norm=norm, single_channel_conv=True),
        )
        self.coarse5 = nn.Sequential(
            GatedConv2d(64, 64, 3, 1, 4, dilation=4, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 4, dilation=4, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 4, dilation=4, activation=activation, norm=norm, single_channel_conv=True),
        )
        self.coarse6 = nn.Sequential(
            GatedConv2d(64, 64, 3, 1, 8, dilation=8, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 8, dilation=8, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 8, dilation=8, activation=activation, norm=norm, single_channel_conv=True),
        )
        self.coarse7 = nn.Sequential(
            GatedConv2d(64, 64, 3, 1, 16, dilation=16, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 16, dilation=16, activation=activation, norm=norm, single_channel_conv=True),
        )
        self.coarse8 = nn.Sequential(
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
        )
        # decoder
        self.coarse9 = nn.Sequential(
            TransposeGatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            TransposeGatedConv2d(64, 32, 3, 1, 1, activation=activation, norm=norm, single_channel_conv=True),
            GatedConv2d(32, 3, 3, 1, 1, activation="none", norm=norm, single_channel_conv=True),
            nn.Tanh(),
        )

    def forward(self, first_in: torch.Tensor) -> torch.Tensor:
        first_out = self.coarse1(first_in)
        first_out = self.coarse2(first_out) + first_out
        first_out = self.coarse3(first_out) + first_out
        first_out = self.coarse4(first_out) + first_out
        first_out = self.coarse5(first_out) + first_out
        first_out = self.coarse6(first_out) + first_out
        first_out = self.coarse7(first_out) + first_out
        first_out = self.coarse8(first_out) + first_out
        first_out = self.coarse9(first_out)
        return torch.clamp(first_out, 0, 1)


class GatedGenerator(nn.Module):
    # def __init__(self, config):
    def __init__(self, norm, activation):
        super().__init__()

        # ######################################### Coarse Network ##################################################
        self.coarse = Coarse(norm, activation)

        # ######################################### Refinement Network ##########################################
        self.refinement1 = nn.Sequential(
            GatedConv2d(3, 32, 5, 2, 2, activation=activation, norm=norm),  # [B,32,256,256]
            GatedConv2d(32, 32, 3, 1, 1, activation=activation, norm=norm),
        )
        self.refinement2 = nn.Sequential(
            # encoder
            GatedConv2d(32, 64, 3, 2, 1, activation=activation, norm=norm),
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm),
        )
        self.refinement3 = nn.Sequential(GatedConv2d(64, 128, 3, 2, 1, activation=activation, norm=norm))
        self.refinement4 = nn.Sequential(
            GatedConv2d(128, 128, 3, 1, 1, activation=activation, norm=norm),
            GatedConv2d(128, 128, 3, 1, 1, activation=activation, norm=norm),
        )
        self.refinement5 = nn.Sequential(
            GatedConv2d(128, 128, 3, 1, 2, dilation=2, activation=activation, norm=norm),
            GatedConv2d(128, 128, 3, 1, 4, dilation=4, activation=activation, norm=norm),
        )
        self.refinement6 = nn.Sequential(
            GatedConv2d(128, 128, 3, 1, 8, dilation=8, activation=activation, norm=norm),
            GatedConv2d(128, 128, 3, 1, 16, dilation=16, activation=activation, norm=norm),
        )
        self.refinement7 = nn.Sequential(
            GatedConv2d(256, 128, 3, 1, 1, activation=activation, norm=norm),
            TransposeGatedConv2d(128, 64, 3, 1, 1, activation=activation, norm=norm),
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm),
        )
        self.refinement8 = nn.Sequential(
            TransposeGatedConv2d(128, 64, 3, 1, 1, activation=activation, norm=norm),
            GatedConv2d(64, 32, 3, 1, 1, activation=activation, norm=norm),
        )
        self.refinement9 = nn.Sequential(
            TransposeGatedConv2d(64, 32, 3, 1, 1, activation=activation, norm=norm),
            GatedConv2d(32, 3, 3, 1, 1, activation="none", norm=norm),
            nn.Tanh(),
        )
        self.conv_pl3 = nn.Sequential(GatedConv2d(128, 128, 3, 1, 1, activation=activation, norm=norm))
        self.conv_pl2 = nn.Sequential(
            GatedConv2d(64, 64, 3, 1, 1, activation=activation, norm=norm),
            GatedConv2d(64, 64, 3, 1, 2, dilation=2, activation=activation, norm=norm),
        )
        self.conv_pl1 = nn.Sequential(
            GatedConv2d(32, 32, 3, 1, 1, activation=activation, norm=norm),
            GatedConv2d(32, 32, 3, 1, 2, dilation=2, activation=activation, norm=norm),
        )

    def forward(self, image: torch.Tensor, mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        img_256 = F.interpolate(image, size=[256, 256], mode="bilinear")
        mask_256 = F.interpolate(mask, size=[256, 256], mode="nearest")  # 1 - hole, 0 - non hole

        first_masked_img = img_256 * (1 - mask_256) + mask_256  # image with hole == 1

        first_in = torch.cat((first_masked_img, mask_256), 1)  # in: [B, 4, H, W]x
        first_out = self.coarse(first_in)  # out: [B, 3, H, W]
        first_out = F.interpolate(first_out, size=[512, 512], mode="bilinear")

        # Refinement
        second_in = image * (1 - mask) + first_out * mask
        pl1 = self.refinement1(second_in)  # out: [B, 32, 256, 256]
        pl2 = self.refinement2(pl1)  # out: [B, 64, 128, 128]
        second_out = self.refinement3(pl2)  # out: [B, 128, 64, 64]
        second_out = self.refinement4(second_out) + second_out  # out: [B, 128, 64, 64]
        second_out = self.refinement5(second_out) + second_out
        pl3 = self.refinement6(second_out) + second_out  # out: [B, 128, 64, 64]
        # Calculate Attention
        patch_fb = self.cal_patch(32, mask, 512)
        att = self.compute_attention(pl3, patch_fb)

        second_out = torch.cat((pl3, self.conv_pl3(self.attention_transfer(pl3, att))), 1)  # out: [B, 256, 64, 64]
        second_out = self.refinement7(second_out)  # out: [B, 64, 128, 128]

        # out: [B, 128, 128, 128]
        second_out = torch.cat((second_out, self.conv_pl2(self.attention_transfer(pl2, att))), 1)

        # out: [B, 32, 256, 256]
        second_out = self.refinement8(second_out)

        # out: [B, 64, 256, 256]
        second_out = torch.cat((second_out, self.conv_pl1(self.attention_transfer(pl1, att))), 1)

        # out: [B, 3, H, W]
        second_out = self.refinement9(second_out)
        second_out = torch.clamp(second_out, 0, 1)
        return first_out, second_out

    @staticmethod
    def cal_patch(patch_num: int, mask: torch.Tensor, raw_size: int) -> torch.Tensor:
        pool = nn.MaxPool2d(raw_size // patch_num)  # patch_num=32
        return pool(mask)  # out: [B, 1, 32, 32]

    def compute_attention(self, feature, patch_fb):  # in: [B, C:128, 64, 64]
        b = feature.shape[0]
        feature = F.interpolate(feature, scale_factor=0.5, mode="bilinear")  # in: [B, C:128, 32, 32]
        p_fb = torch.reshape(patch_fb, [b, 32 * 32, 1])
        p_matrix = torch.bmm(p_fb, (1 - p_fb).permute([0, 2, 1]))
        f = feature.permute([0, 2, 3, 1]).reshape([b, 32 * 32, 128])
        c = self.cosine_matrix(f, f) * p_matrix
        return F.softmax(c, dim=2) * p_matrix

    def attention_transfer(self, feature, attention):  # feature: [B, C, H, W]
        b_num, c, h, w = feature.shape
        f = self.extract_image_patches(feature, 32)
        f = torch.reshape(f, [b_num, f.shape[1] * f.shape[2], -1])
        f = torch.bmm(attention, f)
        f = torch.reshape(f, [b_num, 32, 32, h // 32, w // 32, c])
        f = f.permute([0, 5, 1, 3, 2, 4])
        return torch.reshape(f, [b_num, c, h, w])

    @staticmethod
    def extract_image_patches(img, patch_num):
        b, c, h, w = img.shape
        img = torch.reshape(img, [b, c, patch_num, h // patch_num, patch_num, w // patch_num])
        img = img.permute([0, 2, 4, 3, 5, 1])
        return img

    @staticmethod
    def cosine_matrix(matrix_a, matrix_b):
        _matrixA_matrixB = torch.bmm(matrix_a, matrix_b.permute([0, 2, 1]))
        _matrixA_norm = torch.sqrt((matrix_a * matrix_a).sum(axis=2)).unsqueeze(dim=2)
        _matrixB_norm = torch.sqrt((matrix_b * matrix_b).sum(axis=2)).unsqueeze(dim=2)
        return _matrixA_matrixB / torch.bmm(_matrixA_norm, _matrixB_norm.permute([0, 2, 1]))


class PatchDiscriminator(nn.Module):
    """
    Input: generated image / ground truth and mask
    Output: patch based region, we set 30 * 30
    """

    def __init__(self):
        super().__init__()
        self.block1 = Conv2dLayer(4, 64, 3, 2, 1, activation="lrelu", norm="in", spectral_norm=True)
        self.block2 = Conv2dLayer(64, 128, 3, 2, 1, activation="lrelu", norm="in", spectral_norm=True)
        self.block3 = Conv2dLayer(128, 256, 3, 2, 1, activation="lrelu", norm="in", spectral_norm=True)
        self.block4 = Conv2dLayer(256, 256, 3, 2, 1, activation="lrelu", norm="in", spectral_norm=True)
        self.block5 = Conv2dLayer(256, 256, 3, 2, 1, activation="lrelu", norm="in", spectral_norm=True)
        self.block6 = Conv2dLayer(256, 16, 3, 2, 1, activation="lrelu", norm="in", spectral_norm=True)
        self.block7 = torch.nn.Linear(1024, 1)

    def forward(self, image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        # the input x should contain 4 channels because it is a combination of recon image and mask
        x = torch.cat((image, mask), 1)
        x = self.block1(x)  # out: [B, 64, 256, 256]
        x = self.block2(x)  # out: [B, 128, 128, 128]
        x = self.block3(x)  # out: [B, 256, 64, 64]
        x = self.block4(x)  # out: [B, 256, 32, 32]
        x = self.block5(x)  # out: [B, 256, 16, 16]
        x = self.block6(x)  # out: [B, 256, 8, 8]
        x = x.reshape([x.shape[0], -1])
        return self.block7(x)
