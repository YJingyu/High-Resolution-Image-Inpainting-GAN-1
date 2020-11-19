# High Resolution Image Inpainting Based on GAN

Refactored implamentation of [https://github.com/wangyx240/High-Resolution-Image-Inpainting-GAN](https://github.com/wangyx240/High-Resolution-Image-Inpainting-GAN)

which is an unofficial Pytorch Re-implementation of [https://arxiv.org/abs/2005.09704](Contextual Residual Aggregation for Ultra High-Resolution Image Inpainting)" (CVPR 2020 Oral).

The code is based on implementation of <a href="https://github.com/zhaoyuzhi/deepfillv2">deepfillv2</a>. Thanks for the great job.

The project is still in progress, please feel free to contact me if there is any problem.

## Implementation
Besides Contextual Residual Aggregation(CRA) and Light-Weight GatedConvolution in the paper, also add Residual network structure, SN-PatchGAN in this project.
### Preparing
Before running, please ensure the environment is `Python 3.6` and `PyTorch 1.2.0`.

Dataset: Download <a href="http://places2.csail.mit.edu/download.html">Places365-Standard</a> for Training and Testing.

### Training
```bash
python train.py -c <path_to_config>
```

Default training process uses hinge loss as the D_loss, also provide Wgan-GP in the code.

For input size of 512x512 and GPU with memory of 11GB, recommended batchsize is 4.

### Acknowledgement & Reference

* [https://github.com/zhaoyuzhi/deepfillv2](https://github.com/zhaoyuzhi/deepfillv2)
* [https://github.com/wangyx240/High-Resolution-Image-Inpainting-GAN](https://github.com/wangyx240/High-Resolution-Image-Inpainting-GAN)

```bash
@misc{yi2020contextual,
    title={Contextual Residual Aggregation for Ultra High-Resolution Image Inpainting},
    author={Zili Yi and Qiang Tang and Shekoofeh Azizi and Daesik Jang and Zhan Xu},
    year={2020},
    eprint={2005.09704},
    archivePrefix={arXiv},
    primaryClass={cs.CV}
}
```
```bash
@inproceedings{yu2019free,
  title={Free-form image inpainting with gated convolution},
  author={Yu, Jiahui and Lin, Zhe and Yang, Jimei and Shen, Xiaohui and Lu, Xin and Huang, Thomas S},
  booktitle={Proceedings of the IEEE International Conference on Computer Vision},
  pages={4471--4480},
  year={2019}
}
```
