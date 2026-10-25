# 学信网档案英文版转化器 🎓📚
> 建议使用 edge、chrome 浏览器进行访问，如其一运行异常，请尝试另一个

本工具设计用于将[学信档案](https://my.chsi.com.cn/archive/bab/index.action)一键转化为可用于[GitHub 学生认证](https://education.github.com/discount_requests/application)的英文版文件。

感谢大家的支持！如果该项目对你有帮助的话，请不吝给予⭐️

如在使用的过程中遇到问题，请在 [Issues](https://github.com/Nagi-ovo/CHSI-Converter/issues) 中提出，我们一起尽力解决！

> [!warning]
> 警示：本项目仅供学习研究，不适用于正式场合。请勿用于学籍认证、留学申请等重要用途，后果自负。

## 本项目不会保留你的隐私信息！！！

[新版处理逻辑](app.py)：每次转换使用独立临时目录，处理结束后清理；日志不记录报告内容、原文件名或补充译名，文件不发送到外部翻译服务。

## 如何使用 🛠️

**如果无法正常使用麻烦你发起 Issue :)**

- 在线转换(推荐方式)：访问[网页端](https://www.ez4stu.nagi.fun/)进行一键转换并下载即可，输出保留原布局的英文 PDF；

- 本地转换：需要 Python 3.12 和 `uv`，不再需要 `poppler` 或 LibreOffice；

```bash
git clone https://github.com/Nagi-ovo/CHSI-Converter.git && cd CHSI-Converter
uv sync --locked
uv run app.py
```

- 离线转换（由于模板更新，现已无法正常转换）：GUI版本，同样需要`poppler`切换到"offline"分支或下载已有的Realse，本地运行即可(不建议下载Release，本人当时并未读过skywind大佬的打包秘籍，最后整出依托答辩)。

或者，你也可以通过 Docker 自行部署。建议使用专用用户的 rootless Docker；`deploy.sh` 会构建并启动新版本，检查通过后再切换反向代理。部署细节见 [部署说明](docs/deployment.md)。

当前支持单页 A4《教育部学籍在线验证报告》的原始文字型 PDF。保留原页尺寸、背景、边框、照片、二维码与各行位置，只替换中文文字。英文过长时会在原文字区域内缩小字号，仍放不下时提示补充较短的正式译名。每次只转换一份文件，最大 5 MB，超时 45 秒。

## 可以自主排查的问题（务必阅读） 🐛

- 学校、专业或院系没有翻译：新版收录了 3,053 个高校名称的中英对照，保留历史校名；社区译名未经全面核验，请以学校公布的英文名为准。没有可靠译名时，请在网页中补充正式英文名，也方便保证信息正确。原问题详见[issue#18](https://github.com/Nagi-ovo/CHSI-Converter/issues/18).

- 转换后排版有问题：新版直接在原 PDF 中替换文字；如果遇到不支持的报告或译文放不下，请发起 Issue，并先隐去个人信息，欢迎大佬来 fix。

- 不要修改学信档案原文件的内容；新版可以使用任意 PDF 文件名。旧版文件名问题可见[这个Issue](https://github.com/Nagi-ovo/CHSI-Converter/issues/13)。

- 旧版 Word 文件的问题：[Word 使用了黑色主题+黑色背景，导致白字被浅色背景遮住以为转换失败](https://github.com/Nagi-ovo/CHSI-Converter/issues/7)，我也遇到这过这个问题，属实难绷。

- 个人姓名，请注意 First Name 为名，Last Name 为姓。在修改[profile](https://github.com/settings/profile)和[账单信息](https://github.com/settings/billing/payment_information)时请注意。

- ~~*请选择你的拍屏导师.jpg*~~ 认证网页上传**图片**时不要使用截图，否则会出现`Please use your device camera to submit academic affiliation documents.`错误。解决方案：拍摄打印件或屏幕后上传照片。~~如果出现摩尔纹地狱可以将生成word文件的底纹去掉。~~

- 修改文件名。直接上传文件可能出现`Please select proof type 'Other' for this image.`错误，参照[知乎用户张周怡的方法](https://zhuanlan.zhihu.com/p/665726757)将文件名改为`Certification.jpg`可解决。

## 认证流程 📋

以下保留了原来的申请经验。GitHub 的认证规则可能会变化，请以申请页面的当前提示为准。新版输出 PDF，旧版 Word 的微调步骤不再需要。

参考[知乎用户啦啦啦的回答](https://zhuanlan.zhihu.com/p/618772237)

### 第一步. 个人档案 🗂️

- 在学信网下载学籍验证报告
- 使用本项目，将原始 PDF 报告转化为英文 PDF
- 打开翻译后的文档，核对译名与原报告信息
- 新版不额外添加“remote study”等原报告没有的内容。
  
### 第二步. GitHub 个人简介 🐙

你可以参考下面的示例：(注意，这里我“@Open-BJUT”只是随便加的，并非必须有这部分，写一遍学校名字就够了。)

此外，只是保险起见才使用的实名，并非必须。

![doc-2](https://cdn.jsdelivr.net/gh/Nagi-ovo/picx-images-hosting@master/docs/chsi-converter/doc-2.2rv08cdhhm.jpg)

### 第三步. 申请认证 📱

- 建议使用手机端进行申请，因为后面需要使用镜头拍照，电脑操作不便。
  [点击这里进行认证](https://education.github.com/discount_requests/application)

- 选择“我是学生”
![doc-1](https://cdn.jsdelivr.net/gh/Nagi-ovo/picx-images-hosting@master/docs/chsi-converter/doc-1.9rj9q8mg83.jpg)

- 按照下图进行操作(教育邮箱一般可在学校邮箱中心申请)
![doc-3](https://cdn.jsdelivr.net/gh/Nagi-ovo/picx-images-hosting@master/docs/chsi-converter/doc-3.1e8h4b1osr.jpg)

### 第四步. 提交证明 📸

- 使用手机拍摄电脑上打开的学信网学籍验证报告文档的照片。
- 需要选择对应的证明类型，如果使用了学信认证报告则选择最后一项，在文本框中输入：

```
Ministry of Education online verification report
```

这里要具体情况具体分析，如果验证无法通过，请采用其它方式，这里参考了[Napleon的知乎回答](https://zhuanlan.zhihu.com/p/672294491?utm_psn=1719124334688301057)：

一种可能的方式是在**校园网**环境下，需要使用“学生证”或“录取通知”进行认证，可以对拍摄的图片进行OCR识别、增强(如某全能王)，拖拽到验证材料处。

接下来，就只需要静待消息了，你应该会在几分钟内收到验证结果，如果通过的话，权益一般会在2周内发放。

### 其它

- 旧版部分代码使用了[用python-docx创建浮动图片](https://blog.csdn.net/BF02jgtRS00XKtCx/article/details/111188806)中的方法，感谢文章作者！
- 原来的 Yosemite 色块背景继续保留，作者为 Caitlin Wang，来源：[Simple Desktops](https://simpledesktops.com/browse/desktops/2015/jul/11/yosemite-color-block/)。
- 由于精力有限目前转换后的美观程度一般，实在抱歉，欢迎大佬来优化！

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Nagi-ovo/CHSI-Converter&type=Date)](https://star-history.com/#Nagi-ovo/CHSI-Converter&Date)


