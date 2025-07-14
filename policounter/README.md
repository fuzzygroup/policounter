# policounter

## About

Policounter is an open source crowd counting software designed to take crowd images from a camera, phone or drone and drive a website of images as well as build a data feed for algorithmic consumption.

## Data model explanation

An **Event** takes place in a **Location** and can have a series of **Observations** that include a crowd size **count**

![](https://github.com/fuzzygroup/policounter/blob/main/doc/policounter_datamodel.png)

## Crowd size estimation using lwcc

Policounter tracks several forms of observation, but also allows an observation to be the result of a machine prediciton.  To achieve this end the [LWCC: A LightWeight Crowd Counting library for Python](https://github.com/tersekmatija/lwcc) was employed.

Per the library [documentation](https://github.com/phwolf/lwcc/blob/master/README.md#Models):

LWCC currently offers 4 models (CSRNet, Bayesian crowd counting, DM-Count, SFANet) pretrained on [Shanghai A](https://ieeexplore.ieee.org/document/7780439), [Shanghai B](https://ieeexplore.ieee.org/document/7780439), and [UCF-QNRF](https://www.crcv.ucf.edu/data/ucf-qnrf/) datasets. The following table shows the model name and MAE / MSE result of the available pretrained models on the test sets.

|   Model name |      SHA       |      SHB      |      QNRF       |
| -----------: | :------------: | :-----------: | :-------------: |
|   **CSRNet** | 75.44 / 113.55 | 11.27 / 19.32 | *Not available* |
|      **Bay** | 66.92 / 112.07 | 8.27 / 13.56  | 90.43 / 161.41  |
| **DM-Count** | 61.39 / 98.56  | 7.68 / 12.66  | 88.97 / 154.11  |
|   **SFANet** |*Not available* | 7.05 / 12.18  | *Not available* |

Valid options for *model_name* are written in the first column and thus include: `CSRNet`, `Bay`, `DM-Count`, and `SFANet`.
Valid options for *model_weights* are written in the first row and thus include: `SHA`, `SHB`,  and `QNRF`.

**Note**: Not all *model_weights* are supported with all *model_names*. See the above table for possible combinations.


