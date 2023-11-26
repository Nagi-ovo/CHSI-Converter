# 学信网档案英文版转化器 🎓📚

本工具设计用于将[学信档案](https://my.chsi.com.cn/archive/bab/index.action)一键转化为可用于[GitHub 学生认证](https://education.github.com/discount_requests/application)的英文版文件。

感谢大家的支持！如果该项目对你有帮助的话，请不吝给予⭐️

如在使用的过程中遇到问题，请在 [Issues](https://github.com/Nagi-ovo/CHSI-Converter/issues) 中提出，我们一起尽力解决！

## 如何使用 🛠️

- 本项目使用需要具备`poppler`，在终端输入`pdftotext -v`即可检查，不同操作系统可在google搜索下载方式。

**下面的在线转换网站由于负载问题刚刚崩了，暂时无法使用，最近会找服务器重新部署一下，可以下载到本地自己部署运行一下:)**
- 在线转换(推荐方式)：访问[网页端](http://www.ez4stu.nagi.fun/)进行一键转换并下载即可,排版可以微调；

- 离线转换：。切换到"offline"分支或下载已有的Realse，本地运行即可(不建议下载Release，本人当时并未读过skywind大佬的打包秘籍，最后整出依托答辩)

或者，你也可以通过 Docker 进行部署。

## 认证流程 📋

参考[知乎用户啦啦啦的回答](https://zhuanlan.zhihu.com/p/618772237)

### 第一步. 个人档案 🗂️

- 在学信网下载学籍验证报告
- 使用本项目或有道等提供文档翻译的软件，将 pdf 报告转化为 word 文档
- 打开翻译后的文档，调整至大小合适

### 第二步. GitHub 个人简介 🐙

你可以参考下面的示例：
<img src="https://thatwebsite.oss-cn-hongkong.aliyuncs.com/ez4stu_doc.png">

### 第三步. 申请认证 📱

- 建议使用手机端进行申请，因为需要使用镜头拍照，电脑操作不便。
  [点击这里进行认证](https://education.github.com/discount_requests/application)

- 选择“我是学生”
  <img src="https://thatwebsite.oss-cn-hongkong.aliyuncs.com/doc_1.jpg">

- 按照下图进行操作(教育邮箱一般可在学校邮箱中心申请)
  <img src="https://thatwebsite.oss-cn-hongkong.aliyuncs.com/doc_2.png">

### 第四步. 提交证明 📸

- 使用手机拍摄电脑上打开的学信网学籍验证报告文档的照片。
- 如果需要选择证明类型，选择最后一个，在文本框中输入：

```
Ministry of Education online verification report
```

如果所有方式都不通过，试试其他的英文证明类型。
接下来，就只需要静待消息了，你应该会在几分钟内收到结果。

### 其它

部分代码使用了[用python-docx创建浮动图片](https://blog.csdn.net/BF02jgtRS00XKtCx/article/details/111188806)中的方法，感谢文章作者！
