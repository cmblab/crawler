# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print
import os
from openai import OpenAI
import re
import json
import base64


def main(image_path):
    print("image_path is "+str(image_path))
    api_key = "sk-your-api-key"
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model = "qwen-vl-ocr-latest"
    ai_client = OpenAI(api_key = api_key,base_url = base_url)
    if os.path.exists(image_path):
        print("processing ...")

    else:
        print("image does not exist")

    prompt = f"""
请从图像中提取以下字段并以JSON格式返回：
成交时间、竞得人、交易土地面积、成交地价、地块位置、土地实际用途等信息。

注意事项：
1. 如果字段有多个名称（如"受让单位"也可能叫"竞得人"），请识别相应内容
2. 对于面积字段，请保留单位（如"12345.67㎡"）
3. 对于价格字段，请保留金额和单位（如"1234.56万元"）
4. 如果找不到某个字段，使用null表示
5. 成交时间请转换为"YYYY年M月D日"格式

"""

    print("🤖 正在调用大模型进行 OCR 识别...")
    base64_image = _encode_image(image_path)
    try:
        completion = ai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                            "min_pixels": 28 * 28 * 4,
                            "max_pixels": 28 * 28 * 8192
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        result_text = completion.choices[0].message.content
        print("📄 OCR 返回文本：", result_text)

        # 提取 JSON 结构
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            return json.loads(result_text)

    except json.JSONDecodeError as e:
        print("❌ JSON 解析失败:", e)
        return {}

    except Exception as e:
        print("❌ 识别失败:", e)
        return {}

def _encode_image(image_path):
    """编码图片为base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
