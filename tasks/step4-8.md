## 步骤8：打包与安装程序制作

请提供将程序打包成exe安装包的完整方案。要求：

    使用Nuitka打包（推荐方案），提供完整的打包命令：

        包含--onefile参数生成单文件

        包含--windows-disable-console隐藏控制台

        包含--enable-plugin=pyside6启用PySide6支持

        包含--follow-import-to=src包含所有模块

        包含资源文件（如图标）的打包方法

    提供PyInstaller备选方案命令

    创建Inno Setup脚本（.iss文件）：

        定义安装目录（默认C:\Program Files\应用名）

        创建开始菜单快捷方式

        添加卸载程序

        可选：安装FFmpeg（或检查系统环境变量）

    说明如何将打包后的exe与FFmpeg依赖一起分发

    提供完整的打包流程文档