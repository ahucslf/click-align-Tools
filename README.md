# click-align Tools点标注单应性配准工具箱
本人在科研过程中需要标注大量的图像对的对应点并需要通过计算单应性矩阵配准这两张图像。
因此根据网络上的现有代码通过不断改进最终形成了本工具，现已开源，可按需使用，不得用于商用，本人保留最终解释权。
## keypoints 点位置/挑战标注工具
本标注工具可以通过点击画布中图片内容，存储该点的位置信息，存储在选中的保存目录下，与当前图片同名。

![](https://liufei-img.oss-cn-shanghai.aliyuncs.com/img/202308192055364.png)

提供了挑战标注选项，如果你的任务中没有需要标注的挑战任务，可以直接选择NC，如果有自己的挑战类型，可以在源码中修改。

## warp_lf  单应性矩阵配准工具

本工具可以通过批量选择文件夹进行批量单应性估计配准操作，并且提供随机扭曲操作，以及增加模糊挑战操作。
![](https://liufei-img.oss-cn-shanghai.aliyuncs.com/img/202308192058753.png)

配准需要四个文件夹，分别是图像1的文件夹，图像1的点标注txt存储文件夹，图像2的文件夹，图像2的点标注txt存储文件夹，root指的是这四个文件夹的父文件夹

![](https://liufei-img.oss-cn-shanghai.aliyuncs.com/img/202308192101747.png)

必须要选择root文件夹，后面四个文件夹，若不选择则默认为root文件夹下的四个文件夹，文件名为默认 visible, infrared , visible_point ,infrared_point 。可以在源码中修改。
本工具可以通过随机单应性变换，增加数据的配准多样性。可以通过改变随机扭曲次数的值进行修改。
在超过1次的随机扭曲中，可以通过增加这几次随机扭曲中的挑战类型，增加多样性，分别是运动模糊，高斯模糊，椒盐噪声三种，并给出了三种噪声的程度调节参数。

- 输出模式0 全输出
- 输出模式1 只输出配准后的棋盘格效果图
- 输出模式2 全输出除了配准后的棋盘格效果图

> Acknowledgment：
This work was jointly supported by National Natural Science Foundation of
China (No. 62006002), the Joint Funds of the National Natural Science Foun-
dation of China (No.U20B2068), Natural Science Foundation of Anhui Province
(No. 2208085J18), Natural Science Foundation of Anhui Higher Education In-
stitution (No. 2022AH040014), the University Synergy Innovation Program of
Anhui Province (No. GXXT-2022-033) and Anhui Provincial Colleges Science
Foundation for Distinguished Young Scholars (No. 2022AH020093).
