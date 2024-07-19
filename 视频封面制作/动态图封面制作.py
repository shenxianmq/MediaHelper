from PIL import Image, ImageDraw, ImageFont, ImageSequence
import os
import traceback
import re


class GifTextAdder:
    def __init__(self, image_path):
        self.image_path = image_path

    def crop_and_draw_text_gif(self, text, eng_text, font_size_ratio=0.2):
        try:
            image_path = self.image_path
            # 保存处理后的图像
            image_dir = os.path.dirname(image_path)
            _, ext = os.path.splitext(image_path)
            output_path = os.path.join(image_dir, f"{text}-封面{ext}")
            # if os.path.exists(output_path):
            #     return
            # 打开图像
            gif_image = Image.open(image_path)
            frames = []
            # 迭代每一帧
            for image in ImageSequence.Iterator(gif_image):
                chinese_text = ""
                # 裁剪图像为16:9的比例
                image = image.convert("RGB")
                width, height = image.size
                target_ratio = 16 / 9
                current_ratio = width / height
                if current_ratio > target_ratio:
                    new_width = int(height * target_ratio)
                    left = (width - new_width) // 2
                    right = left + new_width
                    image = image.crop((left, 0, right, height))
                elif current_ratio < target_ratio:
                    new_height = int(width / target_ratio)
                    top = (height - new_height) // 2
                    bottom = top + new_height
                    image = image.crop((0, top, width, bottom))
                width, height = image.size
                new_width = 960
                new_height = int(new_width * height / width)

                # 调整图片大小
                image = image.resize((new_width, new_height))
                width, height = image.size

                draw = ImageDraw.Draw(image)

                # 计算字体大小
                font_size = int(height * font_size_ratio)
                eng_font_size = int(font_size / 2)
                eng_font = font = ImageFont.truetype(
                    "./static/font/方正综艺简体.ttf",
                    eng_font_size,
                )  # 可替换为您喜欢的字体和大小
                font = ImageFont.truetype(
                    "./static/font/方正综艺简体.ttf",
                    font_size,
                )  # 可替换为您喜欢的字体和大小

                eng_text_color = (0, 0, 0)  # 黑色

                text_color = (255, 255, 255)  # 白色
                shadow_color = (0, 0, 0)  # 黑色
                shadow_offset = (5, 5)  # 阴影偏移量

                # 计算文本宽度和高度
                bbox = draw.textbbox((0, 0), eng_text, font=eng_font)
                eng_text_width = bbox[2] - bbox[0]
                eng_text_height = bbox[3] - bbox[1]

                # 创建一个纯白色的图像
                white_height = eng_text_height + 10
                white_image = Image.new(
                    "RGB", (image.width, white_height), (255, 255, 255)
                )

                eng_text_position = (
                    (image.width - eng_text_width) // 2,
                    image.height
                    - white_height
                    + (white_height - eng_text_height) // 2
                    - 5,
                )

                # 将白色图像粘贴到指定区域
                image.paste(white_image, (0, image.height - white_height))

                bbox = draw.textbbox((0, 0), chinese_text, font=eng_font)
                # 计算文本宽度和高度
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # # 确定文本位置
                # text_position = (
                #     (image.width - text_width) // 2,
                #     image.height - text_height - eng_text_height - 30,
                # )

                # 确定文本位置
                text_position = (
                    35,
                    image.height - text_height - eng_text_height - 135,
                )
                # 绘制阴影
                shadow_position = (
                    text_position[0] + shadow_offset[0],
                    text_position[1] + shadow_offset[1],
                )
                chinese_text = self.add_spaces_between_strings(text)

                draw.text(shadow_position, chinese_text, font=font, fill=shadow_color)

                # 绘制文本
                draw.text(
                    eng_text_position, eng_text, font=eng_font, fill=eng_text_color
                )
                draw.text(text_position, chinese_text, font=font, fill=text_color)
                frames.append(image)

                # 保存截取后的 GIF
            frames[0].save(output_path, save_all=True, append_images=frames[1:])
            print("GIF 图像截取成功！")
            return os.path.split(output_path)[-1]
        except:
            print(f"生成封面图片出错:{traceback.format_exc()}")
        # 显示处理后的图像
        # image.show()

    def add_spaces_between_strings(self, input_string):
        # 使用正则表达式在相邻的中文字符之间插入空格
        # result = re.sub(r"(?<=\S)(?=\S)", " ", input_string)
        result = re.sub(r"([\u4e00-\u9fff])", "\\1 ", input_string)
        return result


# 示例用法
gif_text_adder = GifTextAdder("/Users/shenxian/Downloads/港台剧.gif")
text = "日韩电影"  # 水印文本
eng_text = "English Text"  # 英文文本
output_path = gif_text_adder.crop_and_draw_text(text, eng_text)
print("Output path:", output_path)
