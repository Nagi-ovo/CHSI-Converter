# 学信网档案英文版转化器 🎓📚
> 建议使用 edge、chrome 浏览器进行访问，如其一运行异常，请尝试另一个

本工具设计用于将[学信档案](https://my.chsi.com.cn/archive/bab/index.action)一键转化为可用于[GitHub 学生认证](https://education.github.com/discount_requests/application)的英文版文件。

感谢大家的支持！如果该项目对你有帮助的话，请不吝给予⭐️

如在使用的过程中遇到问题，请在 [Issues](https://github.com/Nagi-ovo/CHSI-Converter/issues) 中提出，我们一起尽力解决！

## 本项目不会保留你的隐私信息！！！

https://github.com/Nagi-ovo/CHSI-Converter/blob/6d5a9c70c53c44a0dfb71d635adfe3063c6549fe/utils.py#L250-L261

## 如何使用 🛠️

**如果无法正常使用麻烦你发起 Issue :)**

- 在线转换(推荐方式)：访问[网页端](http://www.ez4stu.nagi.fun/)进行一键转换并下载即可,排版可以微调；

- 本地转换：需要具备`poppler`，在终端输入`pdftotext -v`即可检查，不同操作系统可在google搜索下载方式，MacOS建议使用`brew install poppler`；

- 离线转换：GUI版本，同样需要`poppler`切换到"offline"分支或下载已有的Realse，本地运行即可(不建议下载Release，本人当时并未读过skywind大佬的打包秘籍，最后整出依托答辩)。

或者，你也可以通过 Docker 自行部署，运行项目中的 `deploy.sh` 即可一键部署。

## 可以自主排查的问题（务必阅读） 🐛

- 不要对要传入的学习网档案原文件进行修改，尤其是**文件名**和其中的内容。详情可见[这个Issue](https://github.com/Nagi-ovo/CHSI-Converter/issues/13)。

- [Word 使用了黑色主题+黑色背景，导致白字被浅色背景遮住以为转换失败](https://github.com/Nagi-ovo/CHSI-Converter/issues/7)，属实难绷。

- 个人姓名，请注意First Name为名，Last Name为姓。在修改[profile](https://github.com/settings/profile)和[账单信息](https://github.com/settings/billing/payment_information)时请注意。

- 学校名修改成英文，见[issue#18](https://github.com/Nagi-ovo/CHSI-Converter/issues/18).

- ~~*请选择你的拍屏导师.jpg*~~ 认证网页上传**图片**时不要使用截图，否则会出现`Please use your device camera to submit academic affiliation documents.`错误。解决方案：拍摄打印件或屏幕后上传照片。~~如果出现摩尔纹地狱可以将生成word文件的底纹去掉。~~

- 修改文件名。直接上传文件可能出现`Please select proof type 'Other' for this image.`错误，参照[知乎用户张周怡的方法](https://zhuanlan.zhihu.com/p/665726757)将文件名改为`Certification.jpg`可解决。

## 认证流程 📋

参考[知乎用户啦啦啦的回答](https://zhuanlan.zhihu.com/p/618772237)

### 第一步. 个人档案 🗂️

- 在学信网下载学籍验证报告
- 使用本项目或有道等提供文档翻译的软件，将 pdf 报告转化为 word 文档
- 打开翻译后的文档，调整至大小合适
- 若使用校园网环境(没有科学上网)，则需要在本项目生成的认证文件中删掉“remote study”的字样。
  
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

部分代码使用了[用python-docx创建浮动图片](https://blog.csdn.net/BF02jgtRS00XKtCx/article/details/111188806)中的方法，感谢文章作者！


### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Nagi-ovo/CHSI-Converter&type=Date)](https://star-history.com/#Nagi-ovo/CHSI-Converter&Date)


