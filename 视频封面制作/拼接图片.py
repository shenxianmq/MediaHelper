import os
from PIL import Image


def concatenate_images(folder_path):
    # 获取文件夹内的所有图片文件，并按文件名排序
    image_files = sorted(
        [f for f in os.listdir(folder_path) if f.endswith((".jpg", ".jpeg", ".png"))]
    )

    # 获取尺寸最小的图片作为模板
    template_image = Image.open(os.path.join(folder_path, image_files[0]))
    min_width = template_image.width
    min_height = template_image.height

    # 计算拼接后的图像尺寸
    total_width = min_width * len(image_files)
    max_height = min_height

    # 创建一个空白画布用于拼接图像
    concatenated_image = Image.new("RGB", (total_width, max_height))

    # 遍历所有图片并进行拼接
    for i, image_file in enumerate(image_files):
        image_path = os.path.join(folder_path, image_file)
        image = Image.open(image_path)

        # 调整图片尺寸以匹配模板图像
        image = image.resize((min_width, min_height), Image.ANTIALIAS)

        # 将图片粘贴到拼接图像上
        x_offset = i * min_width
        concatenated_image.paste(image, (x_offset, 0))

    # 保存拼接后的图像在与图片所在文件夹相同的位置
    output_path = os.path.join(folder_path, "output.jpg")
    concatenated_image.save(output_path)

    print(f"拼接完成，保存到 {output_path}")


# 示例用法
folder_path = input("请输入文件夹路径：")
concatenate_images(folder_path)
